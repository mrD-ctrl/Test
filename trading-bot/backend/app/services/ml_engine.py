"""
Trading212 Smart Bot - Self-Learning ML Engine
Implements reinforcement learning for strategy optimization and adaptive trading
"""
import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from loguru import logger
import asyncio

from app.core.config import settings


class MLEngine:
    """
    Self-learning ML engine for trading strategy optimization.
    Features:
    - Reinforcement learning for strategy parameter tuning
    - Pattern recognition from historical trades
    - Adaptive risk management
    - Automatic model retraining
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.trade_history = []
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
        self.strategy_params = {
            'lookback_period': 20,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'stop_loss_pct': settings.STOP_LOSS_PERCENT,
            'take_profit_pct': settings.TAKE_PROFIT_PERCENT,
            'position_size_pct': settings.MAX_POSITION_SIZE_PERCENT
        }
        self.last_retrain_time = datetime.now()
        self.exploration_rate = settings.EXPLORATION_RATE
        self.learning_rate = settings.LEARNING_RATE
        
    async def load_model(self) -> bool:
        """Load existing model or initialize new one"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                with open(settings.MODEL_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    self.strategy_params = data.get('strategy_params', self.strategy_params)
                logger.info(f"Model loaded from {settings.MODEL_PATH}")
                return True
            else:
                logger.info("No existing model found, initializing new model")
                self._initialize_model()
                return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._initialize_model()
            return True
    
    def _initialize_model(self):
        """Initialize a new ML model"""
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=self.learning_rate,
            max_depth=5,
            random_state=42
        )
        logger.info("New ML model initialized")
    
    def save_model(self):
        """Save current model to disk"""
        try:
            os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
            data = {
                'model': self.model,
                'scaler': self.scaler,
                'strategy_params': self.strategy_params,
                'performance_metrics': self.performance_metrics,
                'saved_at': datetime.now().isoformat()
            }
            with open(settings.MODEL_PATH, 'wb') as f:
                pickle.dump(data, f)
            
            # Create backup
            backup_path = os.path.join(
                settings.MODEL_BACKUP_PATH,
                f"model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            )
            os.makedirs(settings.MODEL_BACKUP_PATH, exist_ok=True)
            with open(backup_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Model saved to {settings.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def prepare_features(self, market_data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features from market data for ML model
        Features include:
        - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
        - Price momentum
        - Volume analysis
        - Volatility measures
        """
        df = market_data.copy()
        
        # Calculate technical indicators
        df = self._calculate_rsi(df)
        df = self._calculate_macd(df)
        df = self._calculate_bollinger_bands(df)
        df = self._calculate_momentum(df)
        df = self._calculate_volatility(df)
        df = self._calculate_volume_indicators(df)
        
        # Select features
        feature_columns = [
            'rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'bb_middle',
            'momentum', 'volatility', 'volume_sma_ratio', 'price_sma_ratio'
        ]
        
        # Handle missing values
        df = df.dropna(subset=feature_columns)
        
        if len(df) == 0:
            raise ValueError("Insufficient data for feature calculation")
        
        features = df[feature_columns].values
        
        # Scale features
        if self.model is not None or len(self.trade_history) > 0:
            features = self.scaler.transform(features)
        else:
            features = self.scaler.fit_transform(features)
        
        return features
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std * 2)
        df['bb_lower'] = df['bb_middle'] - (std * 2)
        return df
    
    def _calculate_momentum(self, df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """Calculate price momentum"""
        df['momentum'] = df['close'] / df['close'].shift(period) - 1
        return df
    
    def _calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate rolling volatility"""
        returns = df['close'].pct_change()
        df['volatility'] = returns.rolling(window=period).std()
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        df['volume_sma'] = df['volume'].rolling(window=period).mean()
        df['volume_sma_ratio'] = df['volume'] / df['volume_sma']
        df['price_sma'] = df['close'].rolling(window=period).mean()
        df['price_sma_ratio'] = df['close'] / df['price_sma']
        return df
    
    def predict_signal(self, features: np.ndarray) -> Tuple[int, float]:
        """
        Predict trading signal (1=buy, 0=hold, -1=sell) with confidence
        Implements exploration-exploitation tradeoff for self-learning
        """
        if self.model is None:
            return 0, 0.0
        
        # Exploration: occasionally take random actions to learn
        if np.random.random() < self.exploration_rate:
            action = np.random.choice([-1, 0, 1])
            confidence = 0.5
        else:
            # Exploitation: use model prediction
            prediction = self.model.predict(features.reshape(1, -1))[0]
            probabilities = self.model.predict_proba(features.reshape(1, -1))[0]
            
            # Map prediction to trading signal
            if len(probabilities) == 2:
                action = 1 if prediction == 1 else -1
                confidence = max(probabilities)
            else:
                action = prediction - 1  # Map 0,1,2 to -1,0,1
                confidence = max(probabilities)
        
        return action, confidence
    
    def record_trade(self, trade_data: Dict):
        """Record trade outcome for learning"""
        self.trade_history.append(trade_data)
        
        # Update performance metrics
        self.performance_metrics['total_trades'] += 1
        if trade_data['profit_loss'] > 0:
            self.performance_metrics['winning_trades'] += 1
        else:
            self.performance_metrics['losing_trades'] += 1
        
        self.performance_metrics['total_profit'] += trade_data['profit_loss']
        
        # Check if retraining is needed
        if len(self.trade_history) >= settings.MIN_TRADES_FOR_RETRAIN:
            self._check_and_retrain()
    
    def _check_and_retrain(self):
        """Check if model needs retraining and retrain if necessary"""
        time_since_retrain = datetime.now() - self.last_retrain_time
        hours_since_retrain = time_since_retrain.total_seconds() / 3600
        
        if hours_since_retrain >= settings.RETRAIN_INTERVAL_HOURS:
            logger.info("Retraining ML model with new trade data...")
            self.retrain_model()
            self.last_retrain_time = datetime.now()
    
    def retrain_model(self, market_data: Optional[pd.DataFrame] = None):
        """
        Retrain the ML model with accumulated trade history
        Uses supervised learning on past trades to improve predictions
        """
        if len(self.trade_history) < settings.MIN_TRADES_FOR_RETRAIN:
            logger.warning("Insufficient trade history for retraining")
            return
        
        try:
            # Prepare training data from trade history
            X = []
            y = []
            
            for trade in self.trade_history[-500:]:  # Use last 500 trades
                if 'features' in trade and 'outcome' in trade:
                    X.append(trade['features'])
                    # Outcome: 1 for profitable, 0 for loss
                    y.append(1 if trade['outcome'] > 0 else 0)
            
            if len(X) < 50:
                logger.warning("Not enough valid training samples")
                return
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"Model retrained - Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
            
            # Adjust exploration rate based on performance
            if test_score > 0.6:
                self.exploration_rate = max(0.05, self.exploration_rate * 0.95)
            else:
                self.exploration_rate = min(0.3, self.exploration_rate * 1.1)
            
            # Save updated model
            self.save_model()
            
        except Exception as e:
            logger.error(f"Error during retraining: {e}")
    
    def optimize_strategy_params(self, performance_data: Dict) -> Dict:
        """
        Automatically tune strategy parameters based on performance
        Uses Bayesian optimization approach
        """
        current_params = self.strategy_params.copy()
        
        # Analyze performance
        win_rate = self.performance_metrics['winning_trades'] / max(
            1, self.performance_metrics['total_trades']
        )
        
        # Adjust parameters based on performance
        if win_rate < 0.45:
            # Too many losses - be more conservative
            current_params['stop_loss_pct'] = min(
                5.0, current_params['stop_loss_pct'] * 0.9
            )
            current_params['take_profit_pct'] = max(
                3.0, current_params['take_profit_pct'] * 1.1
            )
            logger.info("Adjusting strategy: More conservative (low win rate)")
        elif win_rate > 0.60:
            # Good performance - can be more aggressive
            current_params['stop_loss_pct'] = max(
                1.0, current_params['stop_loss_pct'] * 1.05
            )
            current_params['take_profit_pct'] = min(
                10.0, current_params['take_profit_pct'] * 0.95
            )
            logger.info("Adjusting strategy: More aggressive (high win rate)")
        
        # Update position sizing based on Sharpe ratio
        if self.performance_metrics['sharpe_ratio'] > 1.5:
            current_params['position_size_pct'] = min(
                10.0, current_params['position_size_pct'] * 1.1
            )
        elif self.performance_metrics['sharpe_ratio'] < 0.5:
            current_params['position_size_pct'] = max(
                1.0, current_params['position_size_pct'] * 0.9
            )
        
        self.strategy_params = current_params
        logger.info(f"Optimized strategy params: {current_params}")
        
        return current_params
    
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        total_trades = self.performance_metrics['total_trades']
        win_rate = (
            self.performance_metrics['winning_trades'] / max(1, total_trades)
        )
        avg_profit = (
            self.performance_metrics['total_profit'] / max(1, total_trades)
        )
        
        return {
            'total_trades': total_trades,
            'winning_trades': self.performance_metrics['winning_trades'],
            'losing_trades': self.performance_metrics['losing_trades'],
            'win_rate': round(win_rate, 3),
            'total_profit_gbp': round(self.performance_metrics['total_profit'], 2),
            'average_profit_per_trade': round(avg_profit, 2),
            'sharpe_ratio': round(self.performance_metrics['sharpe_ratio'], 3),
            'max_drawdown': round(self.performance_metrics['max_drawdown'], 3),
            'current_exploration_rate': round(self.exploration_rate, 3),
            'strategy_parameters': self.strategy_params,
            'last_retrain_time': self.last_retrain_time.isoformat(),
            'model_saved': os.path.exists(settings.MODEL_PATH)
        }


# Singleton instance
ml_engine_instance = None

def get_ml_engine() -> MLEngine:
    """Get or create ML engine singleton"""
    global ml_engine_instance
    if ml_engine_instance is None:
        ml_engine_instance = MLEngine()
    return ml_engine_instance
