"""
Helper utilities for the Django App Operator.
"""


def get_common_labels(app_name: str) -> dict:
    """
    Generate common labels to be applied to all resources.
    
    Args:
        app_name: The name of the DjangoApp resource
        
    Returns:
        Dictionary of labels following Kubernetes recommended labels
    """
    return {
        'app.kubernetes.io/name': 'djangoapp',
        'app.kubernetes.io/instance': app_name,
        'app.kubernetes.io/managed-by': 'djangoapp-operator',
    }


def get_pod_labels(app_name: str) -> dict:
    """
    Generate labels for pods created by the Deployment.
    These are used by Service selectors.
    
    Args:
        app_name: The name of the DjangoApp resource
        
    Returns:
        Dictionary of labels for pod selection
    """
    return {
        'app.kubernetes.io/name': 'djangoapp',
        'app.kubernetes.io/instance': app_name,
    }