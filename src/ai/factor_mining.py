"""
因子挖掘系统 - 基于遗传编程的自动因子发现
Factor Mining System using Genetic Programming
"""

from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger
import operator
import random

# 基础数学运算
OPERATIONS = {
    'add': operator.add,
    'sub': operator.sub,
    'mul': operator.mul,
    'div': lambda x, y: x / y if y != 0 else 0,
    'max': lambda x, y: max(x, y),
    'min': lambda x, y: min(x, y),
}

FUNCTIONS = {
    'abs': np.abs,
    'log': lambda x: np.log(np.abs(x) + 1e-10),
    'exp': lambda x: np.clip(np.exp(x), -1e10, 1e10),
    'sqrt': lambda x: np.sqrt(np.abs(x)),
    'sign': np.sign,
    'rank': lambda x: pd.Series(x).rank(pct=True).values,
}


@dataclass
class FactorConfig:
    """因子配置"""
    # 遗传算法参数
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.2
    crossover_rate: float = 0.7
    elite_ratio: float = 0.1
    
    # 因子评估
    min_ic: float = 0.02           # 最小IC阈值
    lookback_period: int = 252     # 回看期
    
    # 因子约束
    max_depth: int = 5             # 表达式最大深度
    max_features: int = 10         # 最多使用特征数
    

@dataclass
class Factor:
    """因子"""
    name: str
    expression: str
    ic: float                      # 信息系数
    ic_ir: float                   # IC信息比率
    rank_ic: float                 # Rank IC
    turnover: float                # 换手率
    values: Optional[np.ndarray] = None
    

@dataclass
class FactorMiningResult:
    """因子挖掘结果"""
    top_factors: List[Factor]
    all_factors: List[Factor]
    best_factor: Factor
    generation_stats: List[Dict]
    timestamp: str


class ExpressionTree:
    """表达式树节点"""
    
    def __init__(self, value, left=None, right=None, node_type='op'):
        """
        初始化节点
        
        Args:
            value: 节点值 (操作符/函数/特征名/常数)
            left: 左子树
            right: 右子树
            node_type: 节点类型 ('op', 'func', 'feat', 'const')
        """
        self.value = value
        self.left = left
        self.right = right
        self.node_type = node_type
    
    def evaluate(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """
        计算表达式值
        
        Args:
            data: 特征数据字典
            
        Returns:
            计算结果数组
        """
        if self.node_type == 'feat':
            # 特征节点
            return data.get(self.value, np.zeros(len(list(data.values())[0])))
        
        elif self.node_type == 'const':
            # 常数节点
            length = len(list(data.values())[0])
            return np.full(length, self.value)
        
        elif self.node_type == 'func':
            # 函数节点
            if self.left is None:
                return np.zeros(len(list(data.values())[0]))
            
            arg = self.left.evaluate(data)
            
            try:
                return FUNCTIONS[self.value](arg)
            except:
                return np.zeros_like(arg)
        
        elif self.node_type == 'op':
            # 操作符节点
            if self.left is None or self.right is None:
                return np.zeros(len(list(data.values())[0]))
            
            left_val = self.left.evaluate(data)
            right_val = self.right.evaluate(data)
            
            try:
                return OPERATIONS[self.value](left_val, right_val)
            except:
                return np.zeros_like(left_val)
        
        return np.zeros(len(list(data.values())[0]))
    
    def to_string(self) -> str:
        """转换为字符串表达式"""
        if self.node_type == 'feat':
            return self.value
        
        elif self.node_type == 'const':
            return f"{self.value:.2f}"
        
        elif self.node_type == 'func':
            if self.left is None:
                return f"{self.value}(0)"
            return f"{self.value}({self.left.to_string()})"
        
        elif self.node_type == 'op':
            if self.left is None or self.right is None:
                return "0"
            return f"({self.left.to_string()} {self.value} {self.right.to_string()})"
        
        return "0"
    
    def depth(self) -> int:
        """计算树深度"""
        if self.node_type in ['feat', 'const']:
            return 1
        
        left_depth = self.left.depth() if self.left else 0
        right_depth = self.right.depth() if self.right else 0
        
        return 1 + max(left_depth, right_depth)
    
    def copy(self):
        """深拷贝"""
        left_copy = self.left.copy() if self.left else None
        right_copy = self.right.copy() if self.right else None
        return ExpressionTree(self.value, left_copy, right_copy, self.node_type)


class FactorMiner:
    """因子挖掘器"""
    
    def __init__(self, config: Optional[FactorConfig] = None):
        """
        初始化因子挖掘器
        
        Args:
            config: 因子配置
        """
        self.config = config or FactorConfig()
        self.population = []
        self.feature_names = []
        
        logger.info("因子挖掘器初始化完成")
    
    def _create_random_tree(self, 
                           depth: int = 0, 
                           max_depth: Optional[int] = None) -> ExpressionTree:
        """
        创建随机表达式树
        
        Args:
            depth: 当前深度
            max_depth: 最大深度
            
        Returns:
            ExpressionTree
        """
        if max_depth is None:
            max_depth = self.config.max_depth
        
        # 叶子节点条件
        if depth >= max_depth or (depth > 0 and random.random() < 0.3):
            if random.random() < 0.7:
                # 特征节点
                feat = random.choice(self.feature_names)
                return ExpressionTree(feat, node_type='feat')
            else:
                # 常数节点
                const = random.choice([-2, -1, -0.5, 0.5, 1, 2, 10])
                return ExpressionTree(const, node_type='const')
        
        # 内部节点
        if random.random() < 0.7:
            # 操作符节点
            op = random.choice(list(OPERATIONS.keys()))
            left = self._create_random_tree(depth + 1, max_depth)
            right = self._create_random_tree(depth + 1, max_depth)
            return ExpressionTree(op, left, right, node_type='op')
        else:
            # 函数节点
            func = random.choice(list(FUNCTIONS.keys()))
            child = self._create_random_tree(depth + 1, max_depth)
            return ExpressionTree(func, left=child, node_type='func')
    
    def _initialize_population(self):
        """初始化种群"""
        logger.info(f"初始化种群: {self.config.population_size} 个个体")
        
        self.population = []
        for _ in range(self.config.population_size):
            tree = self._create_random_tree()
            self.population.append(tree)
    
    def _calculate_ic(self, 
                     factor_values: np.ndarray, 
                     returns: np.ndarray) -> float:
        """
        计算信息系数 (IC)
        
        Args:
            factor_values: 因子值
            returns: 未来收益率
            
        Returns:
            IC值
        """
        # 移除NaN
        mask = ~(np.isnan(factor_values) | np.isnan(returns) | 
                np.isinf(factor_values) | np.isinf(returns))
        
        if mask.sum() < 10:
            return 0.0
        
        factor_clean = factor_values[mask]
        returns_clean = returns[mask]
        
        # 计算相关系数
        try:
            ic = np.corrcoef(factor_clean, returns_clean)[0, 1]
            return ic if not np.isnan(ic) else 0.0
        except:
            return 0.0
    
    def _calculate_rank_ic(self,
                          factor_values: np.ndarray,
                          returns: np.ndarray) -> float:
        """
        计算Rank IC
        
        Args:
            factor_values: 因子值
            returns: 未来收益率
            
        Returns:
            Rank IC
        """
        mask = ~(np.isnan(factor_values) | np.isnan(returns) | 
                np.isinf(factor_values) | np.isinf(returns))
        
        if mask.sum() < 10:
            return 0.0
        
        factor_clean = factor_values[mask]
        returns_clean = returns[mask]
        
        # Rank转换
        factor_rank = pd.Series(factor_clean).rank(pct=True).values
        returns_rank = pd.Series(returns_clean).rank(pct=True).values
        
        try:
            rank_ic = np.corrcoef(factor_rank, returns_rank)[0, 1]
            return rank_ic if not np.isnan(rank_ic) else 0.0
        except:
            return 0.0
    
    def _evaluate_factor(self,
                        tree: ExpressionTree,
                        data: Dict[str, np.ndarray],
                        returns: np.ndarray) -> Tuple[float, float, float]:
        """
        评估因子质量
        
        Args:
            tree: 表达式树
            data: 特征数据
            returns: 未来收益率
            
        Returns:
            (IC, IC_IR, Rank_IC)
        """
        try:
            # 计算因子值
            factor_values = tree.evaluate(data)
            
            # 滚动计算IC
            window = 20
            ics = []
            
            for i in range(window, len(factor_values)):
                ic = self._calculate_ic(
                    factor_values[i-window:i],
                    returns[i-window:i]
                )
                ics.append(ic)
            
            if len(ics) == 0:
                return 0.0, 0.0, 0.0
            
            # IC均值
            ic_mean = np.mean(ics)
            
            # IC信息比率
            ic_std = np.std(ics)
            ic_ir = ic_mean / ic_std if ic_std > 0 else 0.0
            
            # Rank IC
            rank_ic = self._calculate_rank_ic(factor_values, returns)
            
            return ic_mean, ic_ir, rank_ic
        
        except Exception as e:
            logger.debug(f"因子评估失败: {e}")
            return 0.0, 0.0, 0.0
    
    def _select_parents(self, fitness_scores: List[float]) -> List[ExpressionTree]:
        """
        选择父代 (锦标赛选择)
        
        Args:
            fitness_scores: 适应度得分
            
        Returns:
            父代列表
        """
        # 精英保留
        elite_size = int(self.config.population_size * self.config.elite_ratio)
        sorted_indices = np.argsort(fitness_scores)[::-1]
        
        parents = [self.population[i].copy() for i in sorted_indices[:elite_size]]
        
        # 锦标赛选择
        tournament_size = 3
        while len(parents) < self.config.population_size:
            # 随机选择tournament_size个个体
            candidates = random.sample(range(len(self.population)), tournament_size)
            # 选择适应度最高的
            winner = max(candidates, key=lambda i: fitness_scores[i])
            parents.append(self.population[winner].copy())
        
        return parents
    
    def _crossover(self, parent1: ExpressionTree, parent2: ExpressionTree) -> ExpressionTree:
        """
        交叉操作
        
        Args:
            parent1: 父代1
            parent2: 父代2
            
        Returns:
            子代
        """
        if random.random() > self.config.crossover_rate:
            return parent1.copy()
        
        # 随机选择交叉点
        child = parent1.copy()
        
        # 简单实现：随机替换子树
        if random.random() < 0.5 and child.left is not None:
            child.left = parent2.copy()
        if random.random() < 0.5 and child.right is not None:
            child.right = parent2.copy()
        
        return child
    
    def _mutate(self, tree: ExpressionTree) -> ExpressionTree:
        """
        变异操作
        
        Args:
            tree: 表达式树
            
        Returns:
            变异后的树
        """
        if random.random() > self.config.mutation_rate:
            return tree
        
        # 随机替换子树
        if random.random() < 0.5:
            return self._create_random_tree()
        
        # 修改节点值
        mutated = tree.copy()
        
        if mutated.node_type == 'op':
            mutated.value = random.choice(list(OPERATIONS.keys()))
        elif mutated.node_type == 'func':
            mutated.value = random.choice(list(FUNCTIONS.keys()))
        elif mutated.node_type == 'feat':
            mutated.value = random.choice(self.feature_names)
        elif mutated.node_type == 'const':
            mutated.value = random.choice([-2, -1, -0.5, 0.5, 1, 2, 10])
        
        return mutated
    
    def mine_factors(self,
                    data: pd.DataFrame,
                    target_column: str = 'forward_returns') -> FactorMiningResult:
        """
        挖掘因子
        
        Args:
            data: 包含特征和目标的DataFrame
            target_column: 目标列 (未来收益率)
            
        Returns:
            FactorMiningResult
        """
        logger.info("=" * 60)
        logger.info("开始因子挖掘")
        logger.info("=" * 60)
        
        # 准备数据
        self.feature_names = [col for col in data.columns if col != target_column]
        
        feature_dict = {col: data[col].values for col in self.feature_names}
        returns = data[target_column].values
        
        logger.info(f"特征数量: {len(self.feature_names)}")
        logger.info(f"数据长度: {len(data)}")
        
        # 初始化种群
        self._initialize_population()
        
        generation_stats = []
        all_factors = []
        
        # 遗传算法迭代
        for gen in range(self.config.generations):
            logger.info(f"\n--- 第 {gen+1}/{self.config.generations} 代 ---")
            
            # 评估种群
            fitness_scores = []
            for tree in self.population:
                ic, ic_ir, rank_ic = self._evaluate_factor(tree, feature_dict, returns)
                # 综合适应度 = |IC| + |IC_IR|
                fitness = abs(ic) + abs(ic_ir)
                fitness_scores.append(fitness)
            
            # 统计
            best_idx = np.argmax(fitness_scores)
            best_tree = self.population[best_idx]
            best_ic, best_ic_ir, best_rank_ic = self._evaluate_factor(
                best_tree, feature_dict, returns
            )
            
            stats = {
                'generation': gen + 1,
                'best_fitness': fitness_scores[best_idx],
                'mean_fitness': np.mean(fitness_scores),
                'best_ic': best_ic,
                'best_ic_ir': best_ic_ir,
                'best_expression': best_tree.to_string()
            }
            generation_stats.append(stats)
            
            logger.info(f"最佳适应度: {fitness_scores[best_idx]:.4f}")
            logger.info(f"最佳IC: {best_ic:.4f}, IC_IR: {best_ic_ir:.4f}")
            logger.info(f"最佳表达式: {best_tree.to_string()}")
            
            # 保存优秀因子
            if abs(best_ic) >= self.config.min_ic:
                factor = Factor(
                    name=f"factor_gen{gen+1}",
                    expression=best_tree.to_string(),
                    ic=best_ic,
                    ic_ir=best_ic_ir,
                    rank_ic=best_rank_ic,
                    turnover=0.0,  # 需要额外计算
                    values=best_tree.evaluate(feature_dict)
                )
                all_factors.append(factor)
            
            # 选择父代
            parents = self._select_parents(fitness_scores)
            
            # 生成新种群
            new_population = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1 = self._crossover(parents[i], parents[i+1])
                    child2 = self._crossover(parents[i+1], parents[i])
                    
                    child1 = self._mutate(child1)
                    child2 = self._mutate(child2)
                    
                    new_population.extend([child1, child2])
            
            self.population = new_population[:self.config.population_size]
        
        # 选择top因子
        all_factors.sort(key=lambda f: abs(f.ic), reverse=True)
        top_factors = all_factors[:10]
        best_factor = all_factors[0] if all_factors else None
        
        result = FactorMiningResult(
            top_factors=top_factors,
            all_factors=all_factors,
            best_factor=best_factor,
            generation_stats=generation_stats,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        logger.info("=" * 60)
        logger.info("因子挖掘完成")
        logger.info(f"发现 {len(all_factors)} 个有效因子 (IC >= {self.config.min_ic})")
        if best_factor:
            logger.info(f"\n最佳因子:")
            logger.info(f"  表达式: {best_factor.expression}")
            logger.info(f"  IC: {best_factor.ic:.4f}")
            logger.info(f"  IC_IR: {best_factor.ic_ir:.4f}")
        logger.info("=" * 60)
        
        return result


def calculate_factor_correlation(factors: List[Factor]) -> pd.DataFrame:
    """
    计算因子相关性矩阵
    
    Args:
        factors: 因子列表
        
    Returns:
        相关性矩阵DataFrame
    """
    if not factors or factors[0].values is None:
        return pd.DataFrame()
    
    factor_matrix = np.column_stack([f.values for f in factors])
    corr_matrix = np.corrcoef(factor_matrix.T)
    
    factor_names = [f.name for f in factors]
    corr_df = pd.DataFrame(corr_matrix, 
                          index=factor_names, 
                          columns=factor_names)
    
    return corr_df
