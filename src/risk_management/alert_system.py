"""
警报系统 - 实时监控和多渠道通知
Alert System with Multi-Channel Notifications
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path
from loguru import logger


class AlertLevel(Enum):
    """警报级别"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    CRITICAL = "critical"   # 严重
    EMERGENCY = "emergency" # 紧急


class AlertChannel(Enum):
    """通知渠道"""
    LOG = "log"             # 日志
    EMAIL = "email"         # 邮件
    SMS = "sms"             # 短信
    PUSH = "push"           # 推送通知
    WEBHOOK = "webhook"     # Webhook


@dataclass
class Alert:
    """警报"""
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    category: str                    # 类别: risk, signal, system等
    title: str
    message: str
    data: Dict = field(default_factory=dict)
    channels: List[AlertChannel] = field(default_factory=list)
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'category': self.category,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'channels': [c.value for c in self.channels],
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }


@dataclass
class AlertConfig:
    """警报配置"""
    # 邮件配置
    email_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""
    email_to: List[str] = field(default_factory=list)
    
    # 警报规则
    min_alert_interval: int = 300       # 最小警报间隔 (秒)
    max_alerts_per_hour: int = 10       # 每小时最大警报数
    
    # 级别过滤
    min_level_for_email: AlertLevel = AlertLevel.WARNING
    min_level_for_sms: AlertLevel = AlertLevel.CRITICAL
    
    # 存储
    alert_history_file: str = "data/logs/alert_history.json"
    max_history_days: int = 30


class AlertSystem:
    """警报系统"""
    
    def __init__(self, config: Optional[AlertConfig] = None):
        """
        初始化警报系统
        
        Args:
            config: 警报配置
        """
        self.config = config or AlertConfig()
        
        # 警报历史
        self.alerts: List[Alert] = []
        self.alert_count = 0
        
        # 上次警报时间 (用于限流)
        self.last_alert_time: Dict[str, datetime] = {}
        
        # 小时统计 (用于限流)
        self.hourly_counts: Dict[str, int] = {}  # {hour_key: count}
        
        # 加载历史记录
        self._load_history()
        
        logger.info("警报系统初始化完成")
    
    def trigger(self,
               level: AlertLevel,
               category: str,
               title: str,
               message: str,
               data: Optional[Dict] = None,
               channels: Optional[List[AlertChannel]] = None) -> Optional[Alert]:
        """
        触发警报
        
        Args:
            level: 警报级别
            category: 类别
            title: 标题
            message: 消息
            data: 附加数据
            channels: 通知渠道 (None则自动选择)
            
        Returns:
            Alert 或 None (如果被限流)
        """
        try:
            # 检查限流
            if not self._check_rate_limit(category):
                logger.warning(f"警报被限流: {category} - {title}")
                return None
            
            # 自动选择渠道
            if channels is None:
                channels = self._select_channels(level)
            
            # 创建警报
            alert = Alert(
                alert_id=self._generate_alert_id(),
                timestamp=datetime.now(),
                level=level,
                category=category,
                title=title,
                message=message,
                data=data or {},
                channels=channels
            )
            
            # 发送警报
            self._send_alert(alert)
            
            # 记录
            self.alerts.append(alert)
            self._update_rate_limit(category)
            
            # 定期保存
            if len(self.alerts) % 10 == 0:
                self._save_history()
            
            return alert
            
        except Exception as e:
            logger.error(f"触发警报失败: {e}")
            return None
    
    def _check_rate_limit(self, category: str) -> bool:
        """检查速率限制"""
        now = datetime.now()
        
        # 检查最小间隔
        if category in self.last_alert_time:
            elapsed = (now - self.last_alert_time[category]).total_seconds()
            if elapsed < self.config.min_alert_interval:
                return False
        
        # 检查小时限制
        hour_key = now.strftime("%Y%m%d%H")
        if hour_key in self.hourly_counts:
            if self.hourly_counts[hour_key] >= self.config.max_alerts_per_hour:
                return False
        
        return True
    
    def _update_rate_limit(self, category: str):
        """更新速率限制统计"""
        now = datetime.now()
        
        # 更新最后警报时间
        self.last_alert_time[category] = now
        
        # 更新小时计数
        hour_key = now.strftime("%Y%m%d%H")
        self.hourly_counts[hour_key] = self.hourly_counts.get(hour_key, 0) + 1
        
        # 清理旧的小时统计
        current_hour = int(hour_key)
        old_keys = [k for k in self.hourly_counts.keys() if int(k) < current_hour - 24]
        for k in old_keys:
            del self.hourly_counts[k]
    
    def _select_channels(self, level: AlertLevel) -> List[AlertChannel]:
        """根据级别自动选择渠道"""
        channels = [AlertChannel.LOG]  # 总是记录日志
        
        # 根据级别添加渠道
        if level.value == AlertLevel.INFO.value:
            pass  # 仅日志
        
        elif level.value == AlertLevel.WARNING.value:
            if self.config.email_enabled and level.value >= self.config.min_level_for_email.value:
                channels.append(AlertChannel.EMAIL)
        
        elif level.value == AlertLevel.CRITICAL.value:
            if self.config.email_enabled:
                channels.append(AlertChannel.EMAIL)
            # SMS需要额外配置
        
        elif level.value == AlertLevel.EMERGENCY.value:
            if self.config.email_enabled:
                channels.append(AlertChannel.EMAIL)
            # 紧急情况: 所有可用渠道
        
        return channels
    
    def _send_alert(self, alert: Alert):
        """发送警报到各个渠道"""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.LOG:
                    self._send_to_log(alert)
                elif channel == AlertChannel.EMAIL:
                    self._send_to_email(alert)
                elif channel == AlertChannel.SMS:
                    self._send_to_sms(alert)
                elif channel == AlertChannel.PUSH:
                    self._send_to_push(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_to_webhook(alert)
            except Exception as e:
                logger.error(f"发送警报到 {channel.value} 失败: {e}")
        
        alert.is_sent = True
        alert.sent_at = datetime.now()
    
    def _send_to_log(self, alert: Alert):
        """发送到日志"""
        log_msg = f"[{alert.level.value.upper()}] {alert.category} | {alert.title} | {alert.message}"
        
        if alert.level == AlertLevel.INFO:
            logger.info(log_msg)
        elif alert.level == AlertLevel.WARNING:
            logger.warning(log_msg)
        elif alert.level == AlertLevel.CRITICAL:
            logger.error(log_msg)
        elif alert.level == AlertLevel.EMERGENCY:
            logger.critical(log_msg)
    
    def _send_to_email(self, alert: Alert):
        """发送邮件"""
        if not self.config.email_enabled:
            return
        
        if not self.config.email_from or not self.config.email_to:
            logger.warning("邮件配置不完整，跳过邮件发送")
            return
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            
            # 邮件内容
            html_body = self._create_email_html(alert)
            msg.attach(MIMEText(html_body, 'html'))
            
            # 发送
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_from, self.config.email_password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: {alert.title}")
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
    
    def _create_email_html(self, alert: Alert) -> str:
        """创建邮件HTML内容"""
        level_colors = {
            AlertLevel.INFO: '#17a2b8',
            AlertLevel.WARNING: '#ffc107',
            AlertLevel.CRITICAL: '#dc3545',
            AlertLevel.EMERGENCY: '#d32f2f'
        }
        
        color = level_colors.get(alert.level, '#666')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 4px solid {color};
                    padding: 15px;
                    margin: 20px 0;
                    background-color: #f8f9fa;
                }}
                .alert-header {{
                    color: {color};
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .alert-time {{
                    color: #666;
                    font-size: 12px;
                }}
                .alert-message {{
                    margin: 15px 0;
                    line-height: 1.6;
                }}
                .alert-data {{
                    background-color: #fff;
                    padding: 10px;
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="alert-header">
                    [{alert.level.value.upper()}] {alert.title}
                </div>
                <div class="alert-time">
                    时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br>
                    类别: {alert.category}
                </div>
                <div class="alert-message">
                    {alert.message}
                </div>
        """
        
        if alert.data:
            html += f"""
                <div class="alert-data">
                    <strong>详细数据:</strong><br>
                    {json.dumps(alert.data, indent=2, ensure_ascii=False)}
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_to_sms(self, alert: Alert):
        """发送短信"""
        logger.info(f"[SMS] {alert.title}: {alert.message}")
        # 实际实现需要集成短信服务商API
        logger.warning("SMS功能未实现，需要集成短信服务商")
    
    def _send_to_push(self, alert: Alert):
        """发送推送通知"""
        logger.info(f"[PUSH] {alert.title}: {alert.message}")
        # 实际实现需要集成推送服务
        logger.warning("PUSH功能未实现，需要集成推送服务")
    
    def _send_to_webhook(self, alert: Alert):
        """发送到Webhook"""
        logger.info(f"[WEBHOOK] {alert.title}: {alert.message}")
        # 实际实现需要发送HTTP请求
        logger.warning("Webhook功能未实现")
    
    def get_alerts(self,
                  level: Optional[AlertLevel] = None,
                  category: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  limit: int = 100) -> List[Alert]:
        """
        获取警报列表
        
        Args:
            level: 过滤级别
            category: 过滤类别
            start_time: 开始时间
            limit: 最大数量
            
        Returns:
            警报列表
        """
        filtered = self.alerts
        
        # 过滤级别
        if level:
            filtered = [a for a in filtered if a.level == level]
        
        # 过滤类别
        if category:
            filtered = [a for a in filtered if a.category == category]
        
        # 过滤时间
        if start_time:
            filtered = [a for a in filtered if a.timestamp >= start_time]
        
        # 排序并限制数量
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered[:limit]
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """
        获取统计信息
        
        Args:
            hours: 统计最近N小时
            
        Returns:
            统计字典
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alerts if a.timestamp >= cutoff]
        
        # 按级别统计
        by_level = {}
        for level in AlertLevel:
            count = sum(1 for a in recent_alerts if a.level == level)
            by_level[level.value] = count
        
        # 按类别统计
        by_category = {}
        for alert in recent_alerts:
            by_category[alert.category] = by_category.get(alert.category, 0) + 1
        
        return {
            'total': len(recent_alerts),
            'by_level': by_level,
            'by_category': by_category,
            'time_range': f'最近{hours}小时'
        }
    
    def clear_old_alerts(self):
        """清理旧警报"""
        cutoff = datetime.now() - timedelta(days=self.config.max_history_days)
        old_count = len(self.alerts)
        
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff]
        
        removed = old_count - len(self.alerts)
        if removed > 0:
            logger.info(f"清理了 {removed} 条旧警报")
            self._save_history()
    
    def _save_history(self):
        """保存警报历史"""
        try:
            history_file = Path(self.config.alert_history_file)
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [a.to_dict() for a in self.alerts]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"警报历史已保存: {len(data)}条")
            
        except Exception as e:
            logger.error(f"保存警报历史失败: {e}")
    
    def _load_history(self):
        """加载警报历史"""
        try:
            history_file = Path(self.config.alert_history_file)
            
            if not history_file.exists():
                logger.debug("警报历史文件不存在，从空开始")
                return
            
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重建Alert对象
            for item in data:
                alert = Alert(
                    alert_id=item['alert_id'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    level=AlertLevel(item['level']),
                    category=item['category'],
                    title=item['title'],
                    message=item['message'],
                    data=item.get('data', {}),
                    channels=[AlertChannel(c) for c in item.get('channels', [])],
                    is_sent=item.get('is_sent', False),
                    sent_at=datetime.fromisoformat(item['sent_at']) if item.get('sent_at') else None
                )
                self.alerts.append(alert)
            
            logger.info(f"加载了 {len(self.alerts)} 条警报历史")
            
        except Exception as e:
            logger.error(f"加载警报历史失败: {e}")
    
    def _generate_alert_id(self) -> str:
        """生成警报ID"""
        self.alert_count += 1
        return f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.alert_count:04d}"
    
    # 便捷方法
    def info(self, category: str, title: str, message: str, **kwargs):
        """发送信息级警报"""
        return self.trigger(AlertLevel.INFO, category, title, message, **kwargs)
    
    def warning(self, category: str, title: str, message: str, **kwargs):
        """发送警告级警报"""
        return self.trigger(AlertLevel.WARNING, category, title, message, **kwargs)
    
    def critical(self, category: str, title: str, message: str, **kwargs):
        """发送严重警报"""
        return self.trigger(AlertLevel.CRITICAL, category, title, message, **kwargs)
    
    def emergency(self, category: str, title: str, message: str, **kwargs):
        """发送紧急警报"""
        return self.trigger(AlertLevel.EMERGENCY, category, title, message, **kwargs)


# 全局警报系统实例
_alert_system: Optional[AlertSystem] = None


def get_alert_system() -> AlertSystem:
    """获取全局警报系统"""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system


def init_alert_system(config: AlertConfig):
    """初始化全局警报系统"""
    global _alert_system
    _alert_system = AlertSystem(config)
    return _alert_system
