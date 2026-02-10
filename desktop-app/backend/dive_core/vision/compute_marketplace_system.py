#!/usr/bin/env python3
"""
Compute as Currency - Marketplace System
Pioneer in the compute economy
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class ComputeResource:
    """Compute resource specification"""
    resource_id: str
    resource_type: str  # GPU, TPU, CPU
    model: str  # A100, H100, TPU v5
    quantity: int
    memory_gb: int
    flops_tflop: float
    power_watts: int
    availability: float  # 0-1
    location: str
    provider: str


@dataclass
class ComputePrice:
    """Compute pricing"""
    resource_id: str
    price_per_hour: float
    price_per_tflop: float
    price_per_gb_memory: float
    currency: str
    timestamp: str


@dataclass
class ComputeOrder:
    """Compute order"""
    order_id: str
    buyer_id: str
    resource_id: str
    quantity: int
    duration_hours: float
    total_price: float
    status: str  # pending, active, completed
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]


@dataclass
class ComputeMarketMetrics:
    """Market metrics"""
    total_supply_tflop: float
    total_demand_tflop: float
    utilization_rate: float
    average_price_per_tflop: float
    market_cap: float
    trading_volume: float
    timestamp: str


# ========== COMPUTE RESOURCES DATABASE ==========

class ComputeResourcesDB:
    """Database of compute resources"""
    
    def __init__(self):
        self.resources = self._initialize_resources()
        logger.info(f"Initialized Compute Resources DB with {len(self.resources)} resources")
    
    def _initialize_resources(self) -> Dict[str, ComputeResource]:
        """Initialize compute resources"""
        
        resources = {
            'gpu-a100-us-east': ComputeResource(
                resource_id='gpu-a100-us-east',
                resource_type='GPU',
                model='A100',
                quantity=100,
                memory_gb=80,
                flops_tflop=312,
                power_watts=250,
                availability=0.95,
                location='US-East',
                provider='AWS'
            ),
            'gpu-h100-us-west': ComputeResource(
                resource_id='gpu-h100-us-west',
                resource_type='GPU',
                model='H100',
                quantity=50,
                memory_gb=80,
                flops_tflop=989,
                power_watts=350,
                availability=0.92,
                location='US-West',
                provider='Google Cloud'
            ),
            'tpu-v5-asia': ComputeResource(
                resource_id='tpu-v5-asia',
                resource_type='TPU',
                model='TPU v5',
                quantity=32,
                memory_gb=128,
                flops_tflop=2000,
                power_watts=400,
                availability=0.98,
                location='Asia',
                provider='Google Cloud'
            ),
            'cpu-32core-eu': ComputeResource(
                resource_id='cpu-32core-eu',
                resource_type='CPU',
                model='32-Core',
                quantity=200,
                memory_gb=256,
                flops_tflop=10,
                power_watts=100,
                availability=0.99,
                location='EU',
                provider='Azure'
            ),
            'gpu-rtx-decentralized': ComputeResource(
                resource_id='gpu-rtx-decentralized',
                resource_type='GPU',
                model='RTX 4090',
                quantity=1000,
                memory_gb=24,
                flops_tflop=82,
                power_watts=450,
                availability=0.70,
                location='Decentralized',
                provider='Render Network'
            )
        }
        
        return resources
    
    def get_resource(self, resource_id: str) -> Optional[ComputeResource]:
        """Get resource by ID"""
        return self.resources.get(resource_id)
    
    def get_all_resources(self) -> List[ComputeResource]:
        """Get all resources"""
        return list(self.resources.values())
    
    def get_resources_by_type(self, resource_type: str) -> List[ComputeResource]:
        """Get resources by type"""
        return [r for r in self.resources.values() if r.resource_type == resource_type]


# ========== PRICING ENGINE ==========

class PricingEngine:
    """Dynamic pricing for compute resources"""
    
    def __init__(self):
        self.prices = {}
        self.price_history = defaultdict(list)
        self._initialize_prices()
        
        logger.info("Initialized Pricing Engine")
    
    def _initialize_prices(self):
        """Initialize base prices"""
        
        base_prices = {
            'gpu-a100-us-east': {
                'price_per_hour': 3.00,
                'price_per_tflop': 0.0096,
                'price_per_gb_memory': 0.0375
            },
            'gpu-h100-us-west': {
                'price_per_hour': 5.00,
                'price_per_tflop': 0.0051,
                'price_per_gb_memory': 0.0625
            },
            'tpu-v5-asia': {
                'price_per_hour': 8.00,
                'price_per_tflop': 0.0040,
                'price_per_gb_memory': 0.0625
            },
            'cpu-32core-eu': {
                'price_per_hour': 0.50,
                'price_per_tflop': 0.0500,
                'price_per_gb_memory': 0.0020
            },
            'gpu-rtx-decentralized': {
                'price_per_hour': 0.50,
                'price_per_tflop': 0.0061,
                'price_per_gb_memory': 0.0208
            }
        }
        
        for resource_id, price_data in base_prices.items():
            self.prices[resource_id] = ComputePrice(
                resource_id=resource_id,
                price_per_hour=price_data['price_per_hour'],
                price_per_tflop=price_data['price_per_tflop'],
                price_per_gb_memory=price_data['price_per_gb_memory'],
                currency='USD',
                timestamp=datetime.now().isoformat()
            )
    
    def calculate_price(self, resource: ComputeResource, duration_hours: float,
                       quantity: int = 1) -> float:
        """Calculate total price for compute order"""
        
        price = self.prices.get(resource.resource_id)
        if not price:
            return 0
        
        # Base price
        base_total = price.price_per_hour * duration_hours * quantity
        
        # Apply dynamic pricing based on demand
        demand_factor = self._get_demand_factor(resource.resource_id)
        
        # Apply availability discount
        availability_factor = 1.0 - (1.0 - resource.availability) * 0.1
        
        total_price = base_total * demand_factor * availability_factor
        
        return round(total_price, 2)
    
    def _get_demand_factor(self, resource_id: str) -> float:
        """Get demand-based price multiplier"""
        
        # Simulated demand factor (1.0 = normal, 1.5 = high demand)
        demand_factors = {
            'gpu-a100-us-east': 1.3,
            'gpu-h100-us-west': 1.5,
            'tpu-v5-asia': 1.4,
            'cpu-32core-eu': 1.0,
            'gpu-rtx-decentralized': 0.8
        }
        
        return demand_factors.get(resource_id, 1.0)
    
    def update_price(self, resource_id: str, new_price: float):
        """Update price for resource"""
        
        if resource_id in self.prices:
            old_price = self.prices[resource_id].price_per_hour
            self.prices[resource_id].price_per_hour = new_price
            self.prices[resource_id].timestamp = datetime.now().isoformat()
            
            # Record history
            self.price_history[resource_id].append({
                'timestamp': datetime.now().isoformat(),
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': (new_price - old_price) / old_price * 100
            })
            
            logger.info(f"Updated price for {resource_id}: ${old_price} → ${new_price}")


# ========== MARKETPLACE ==========

class ComputeMarketplace:
    """Compute marketplace"""
    
    def __init__(self, resources_db: ComputeResourcesDB, pricing_engine: PricingEngine):
        self.resources_db = resources_db
        self.pricing_engine = pricing_engine
        
        self.orders = {}
        self.order_counter = 0
        self.completed_orders = []
        
        logger.info("Initialized Compute Marketplace")
    
    def place_order(self, buyer_id: str, resource_id: str, 
                   quantity: int, duration_hours: float) -> Optional[ComputeOrder]:
        """Place compute order"""
        
        resource = self.resources_db.get_resource(resource_id)
        if not resource:
            logger.warning(f"Resource {resource_id} not found")
            return None
        
        # Check availability
        if quantity > resource.quantity * resource.availability:
            logger.warning(f"Insufficient availability for {resource_id}")
            return None
        
        # Calculate price
        total_price = self.pricing_engine.calculate_price(resource, duration_hours, quantity)
        
        # Create order
        self.order_counter += 1
        order_id = f"order-{self.order_counter}"
        
        order = ComputeOrder(
            order_id=order_id,
            buyer_id=buyer_id,
            resource_id=resource_id,
            quantity=quantity,
            duration_hours=duration_hours,
            total_price=total_price,
            status='pending',
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None
        )
        
        self.orders[order_id] = order
        
        logger.info(f"Order {order_id} placed: {quantity}x {resource_id} for ${total_price}")
        
        return order
    
    def execute_order(self, order_id: str) -> bool:
        """Execute pending order"""
        
        order = self.orders.get(order_id)
        if not order or order.status != 'pending':
            return False
        
        order.status = 'active'
        order.started_at = datetime.now().isoformat()
        
        logger.info(f"Order {order_id} activated")
        
        return True
    
    def complete_order(self, order_id: str) -> bool:
        """Complete active order"""
        
        order = self.orders.get(order_id)
        if not order or order.status != 'active':
            return False
        
        order.status = 'completed'
        order.completed_at = datetime.now().isoformat()
        
        self.completed_orders.append(order)
        
        logger.info(f"Order {order_id} completed")
        
        return True
    
    def get_market_metrics(self) -> ComputeMarketMetrics:
        """Get market metrics"""
        
        # Calculate total supply
        total_supply_tflop = sum(
            r.flops_tflop * r.quantity * r.availability
            for r in self.resources_db.get_all_resources()
        )
        
        # Calculate total demand (active orders)
        total_demand_tflop = sum(
            self.resources_db.get_resource(o.resource_id).flops_tflop * o.quantity
            for o in self.orders.values() if o.status == 'active'
        )
        
        # Calculate utilization
        utilization_rate = total_demand_tflop / total_supply_tflop if total_supply_tflop > 0 else 0
        
        # Calculate average price
        all_prices = [p.price_per_tflop for p in self.pricing_engine.prices.values()]
        average_price_per_tflop = np.mean(all_prices) if all_prices else 0
        
        # Calculate market cap
        market_cap = total_supply_tflop * average_price_per_tflop * 24 * 365  # Annual
        
        # Calculate trading volume
        trading_volume = sum(o.total_price for o in self.completed_orders)
        
        metrics = ComputeMarketMetrics(
            total_supply_tflop=total_supply_tflop,
            total_demand_tflop=total_demand_tflop,
            utilization_rate=utilization_rate,
            average_price_per_tflop=average_price_per_tflop,
            market_cap=market_cap,
            trading_volume=trading_volume,
            timestamp=datetime.now().isoformat()
        )
        
        return metrics
    
    def get_price_trends(self, resource_id: str, days: int = 7) -> Dict:
        """Get price trends"""
        
        history = self.pricing_engine.price_history.get(resource_id, [])
        
        if not history:
            return {'resource_id': resource_id, 'history': []}
        
        # Get recent history
        recent = history[-days:] if len(history) > days else history
        
        return {
            'resource_id': resource_id,
            'history': recent,
            'avg_price': np.mean([h['new_price'] for h in recent]),
            'min_price': min([h['new_price'] for h in recent]),
            'max_price': max([h['new_price'] for h in recent])
        }


# ========== COMPUTE DERIVATIVES ==========

class ComputeDerivatives:
    """Compute derivatives for hedging and speculation"""
    
    def __init__(self, marketplace: ComputeMarketplace):
        self.marketplace = marketplace
        self.futures = {}
        self.options = {}
        
        logger.info("Initialized Compute Derivatives")
    
    def create_future(self, resource_id: str, expiration_date: str,
                     strike_price: float, quantity: int) -> str:
        """Create compute future contract"""
        
        future_id = f"future-{len(self.futures)}"
        
        self.futures[future_id] = {
            'resource_id': resource_id,
            'expiration_date': expiration_date,
            'strike_price': strike_price,
            'quantity': quantity,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        logger.info(f"Created future {future_id}: {quantity}x {resource_id} @ ${strike_price}")
        
        return future_id
    
    def create_option(self, resource_id: str, expiration_date: str,
                     strike_price: float, option_type: str, premium: float) -> str:
        """Create compute option contract"""
        
        option_id = f"option-{len(self.options)}"
        
        self.options[option_id] = {
            'resource_id': resource_id,
            'expiration_date': expiration_date,
            'strike_price': strike_price,
            'option_type': option_type,  # call or put
            'premium': premium,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        logger.info(f"Created {option_type} option {option_id}: {resource_id} @ ${strike_price} (premium: ${premium})")
        
        return option_id


# ========== MAIN ==========

def main():
    """Example usage"""
    
    logger.info("="*80)
    logger.info("COMPUTE AS CURRENCY - MARKETPLACE SYSTEM")
    logger.info("="*80)
    
    # Initialize system
    resources_db = ComputeResourcesDB()
    pricing_engine = PricingEngine()
    marketplace = ComputeMarketplace(resources_db, pricing_engine)
    derivatives = ComputeDerivatives(marketplace)
    
    # 1. Display available resources
    logger.info("\n1. AVAILABLE COMPUTE RESOURCES:")
    logger.info("="*80)
    
    for resource in resources_db.get_all_resources():
        price = pricing_engine.prices.get(resource.resource_id)
        logger.info(f"{resource.resource_id:30s} | Type: {resource.resource_type:4s} | "
                   f"Qty: {resource.quantity:4d} | TFLOP: {resource.flops_tflop:7.0f} | "
                   f"Price: ${price.price_per_hour:.2f}/hr")
    
    # 2. Place orders
    logger.info("\n2. PLACING COMPUTE ORDERS:")
    logger.info("="*80)
    
    orders = []
    
    # Order 1: GPU A100 for AI training
    order1 = marketplace.place_order('buyer-001', 'gpu-a100-us-east', 10, 24)
    if order1:
        orders.append(order1)
        logger.info(f"Order 1: 10x A100 for 24 hours = ${order1.total_price}")
    
    # Order 2: TPU v5 for inference
    order2 = marketplace.place_order('buyer-002', 'tpu-v5-asia', 5, 168)
    if order2:
        orders.append(order2)
        logger.info(f"Order 2: 5x TPU v5 for 168 hours = ${order2.total_price}")
    
    # Order 3: Decentralized GPU
    order3 = marketplace.place_order('buyer-003', 'gpu-rtx-decentralized', 50, 1)
    if order3:
        orders.append(order3)
        logger.info(f"Order 3: 50x RTX 4090 for 1 hour = ${order3.total_price}")
    
    # 3. Execute and complete orders
    logger.info("\n3. EXECUTING ORDERS:")
    logger.info("="*80)
    
    for order in orders:
        marketplace.execute_order(order.order_id)
        marketplace.complete_order(order.order_id)
        logger.info(f"Order {order.order_id} executed and completed")
    
    # 4. Market metrics
    logger.info("\n4. MARKET METRICS:")
    logger.info("="*80)
    
    metrics = marketplace.get_market_metrics()
    
    logger.info(f"Total Supply: {metrics.total_supply_tflop:,.0f} TFLOP")
    logger.info(f"Total Demand: {metrics.total_demand_tflop:,.0f} TFLOP")
    logger.info(f"Utilization: {metrics.utilization_rate:.1%}")
    logger.info(f"Avg Price: ${metrics.average_price_per_tflop:.6f}/TFLOP")
    logger.info(f"Market Cap: ${metrics.market_cap:,.0f}")
    logger.info(f"Trading Volume: ${metrics.trading_volume:,.2f}")
    
    # 5. Derivatives
    logger.info("\n5. COMPUTE DERIVATIVES:")
    logger.info("="*80)
    
    # Create futures
    future1 = derivatives.create_future('gpu-h100-us-west', '2026-03-31', 5.50, 100)
    future2 = derivatives.create_future('tpu-v5-asia', '2026-06-30', 8.50, 50)
    
    # Create options
    call_option = derivatives.create_option('gpu-a100-us-east', '2026-02-28', 3.50, 'call', 0.25)
    put_option = derivatives.create_option('gpu-rtx-decentralized', '2026-02-28', 0.45, 'put', 0.05)
    
    # 6. Pricing strategy
    logger.info("\n6. DYNAMIC PRICING:")
    logger.info("="*80)
    
    logger.info("Current prices:")
    for resource_id, price in pricing_engine.prices.items():
        logger.info(f"{resource_id:30s}: ${price.price_per_hour:.2f}/hr (${price.price_per_tflop:.6f}/TFLOP)")
    
    logger.info("\nUpdating prices based on demand...")
    pricing_engine.update_price('gpu-h100-us-west', 5.50)
    pricing_engine.update_price('tpu-v5-asia', 8.50)
    
    logger.info("\n" + "="*80)
    logger.info("COMPUTE MARKETPLACE READY - PIONEER THE COMPUTE ECONOMY!")
    logger.info("="*80)


if __name__ == "__main__":
    main()
