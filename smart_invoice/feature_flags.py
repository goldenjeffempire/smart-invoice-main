"""
Smart Invoice - Feature Flags System
Enables gradual rollout, A/B testing, and feature toggles
"""
import logging
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class FeatureFlagManager:
    """
    Centralized feature flag management with caching.
    Supports percentage rollouts, user targeting, and A/B testing.
    """
    
    # Default flag definitions (immutable reference)
    _DEFAULT_FLAGS_TEMPLATE = {
        # Landing page experiments
        'hero_variant_gradient': {
            'enabled': True,
            'rollout_percentage': 100,
            'description': 'New gradient hero section on landing page'
        },
        'enhanced_pricing_matrix': {
            'enabled': True,
            'rollout_percentage': 100,
            'description': 'Enhanced pricing comparison matrix'
        },
        'newsletter_capture': {
            'enabled': True,
            'rollout_percentage': 100,
            'description': 'Newsletter signup form'
        },
        'analytics_events': {
            'enabled': True,
            'rollout_percentage': 100,
            'description': 'Track user interactions for analytics'
        },
        
        # Feature experiments
        'invoice_templates_v2': {
            'enabled': False,
            'rollout_percentage': 0,
            'description': 'Next-gen invoice templates'
        },
        'multi_currency': {
            'enabled': False,
            'rollout_percentage': 0,
            'description': 'Multi-currency support'
        },
        'recurring_invoices': {
            'enabled': False,
            'rollout_percentage': 0,
            'description': 'Recurring invoice automation'
        },
        
        # Performance features
        'redis_cache': {
            'enabled': True,
            'rollout_percentage': 100,
            'description': 'Use Redis for caching'
        },
        'database_read_replica': {
            'enabled': False,
            'rollout_percentage': 0,
            'description': 'Use read replica for analytics queries'
        },
    }
    
    def __init__(self):
        """Initialize feature flag manager."""
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        """Load flags from cache or default configuration."""
        cached_flags = cache.get('feature_flags')
        if cached_flags:
            return cached_flags
        
        # Load from settings or use defaults (deep copy to prevent mutation)
        import copy
        default_flags = getattr(settings, 'FEATURE_FLAGS', self._DEFAULT_FLAGS_TEMPLATE)
        flags = copy.deepcopy(default_flags)
        cache.set('feature_flags', flags, timeout=300)  # Cache for 5 minutes
        return flags
    
    def is_enabled(self, flag_name: str, user=None, request=None) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag_name: Name of the feature flag
            user: User object (for user-specific targeting)
            request: Request object (for A/B testing based on session)
            
        Returns:
            True if flag is enabled, False otherwise
        """
        if flag_name not in self.flags:
            logger.warning(f"Unknown feature flag: {flag_name}")
            return False
        
        flag = self.flags[flag_name]
        
        # Check if flag is globally enabled
        if not flag.get('enabled', False):
            return False
        
        # Check rollout percentage
        rollout = flag.get('rollout_percentage', 100)
        if rollout < 100:
            # Use user ID or session ID for consistent bucketing
            if user and hasattr(user, 'id'):
                bucket = user.id % 100
            elif request and hasattr(request, 'session'):
                session_key = request.session.session_key or ''
                bucket = sum(ord(c) for c in session_key) % 100
            else:
                # Random bucketing for anonymous users
                import random
                bucket = random.randint(0, 99)
            
            if bucket >= rollout:
                return False
        
        # Check user targeting (if specified)
        target_users = flag.get('target_users', [])
        if target_users and user:
            user_id = getattr(user, 'id', None)
            username = getattr(user, 'username', None)
            
            if user_id not in target_users and username not in target_users:
                return False
        
        return True
    
    def set_flag(self, flag_name: str, enabled: bool, rollout_percentage: int = 100):
        """
        Set a feature flag value.
        
        Args:
            flag_name: Name of the feature flag
            enabled: Whether the flag is enabled
            rollout_percentage: Percentage of users to enable for (0-100)
        """
        if flag_name not in self.flags:
            self.flags[flag_name] = {}
        
        self.flags[flag_name]['enabled'] = enabled
        self.flags[flag_name]['rollout_percentage'] = rollout_percentage
        
        # Update cache
        cache.set('feature_flags', self.flags, timeout=300)
        logger.info(f"Feature flag updated: {flag_name} = {enabled} ({rollout_percentage}%)")
    
    def get_variant(self, flag_name: str, user=None, request=None) -> Optional[str]:
        """
        Get A/B test variant for a flag.
        
        Args:
            flag_name: Name of the feature flag
            user: User object
            request: Request object
            
        Returns:
            Variant name ('control' or 'variant') or None if flag is disabled
        """
        if not self.is_enabled(flag_name, user, request):
            return None
        
        flag = self.flags.get(flag_name, {})
        
        # If no variants defined, return 'variant' (feature is enabled)
        if 'variants' not in flag:
            return 'variant'
        
        # Consistent bucketing for A/B testing
        if user and hasattr(user, 'id'):
            bucket = user.id % 100
        elif request and hasattr(request, 'session'):
            session_key = request.session.session_key or ''
            bucket = sum(ord(c) for c in session_key) % 100
        else:
            import random
            bucket = random.randint(0, 99)
        
        # Determine variant based on bucket
        variants = flag['variants']
        cumulative = 0
        for variant_name, percentage in variants.items():
            cumulative += percentage
            if bucket < cumulative:
                return variant_name
        
        return 'control'
    
    def refresh(self):
        """Refresh flags from cache/settings."""
        cache.delete('feature_flags')
        self.flags = self._load_flags()
        logger.info("Feature flags refreshed")


# Global instance
feature_flags = FeatureFlagManager()
