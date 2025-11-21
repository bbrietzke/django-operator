"""
HPABuilder - Creates Kubernetes HorizontalPodAutoscaler resources.
"""


class HPABuilder:
    """
    Builds a Kubernetes HorizontalPodAutoscaler resource.
    
    The HPA manages automatic scaling of the Deployment based on CPU utilization.
    """
    
    def __init__(self, name: str, namespace: str, min_replicas: int, 
                 max_replicas: int, target_cpu_percentage: int, labels: dict):
        """
        Initialize the HPABuilder.
        
        Args:
            name: Name of the DjangoApp (will create {name}-hpa, target {name}-deployment)
            namespace: Kubernetes namespace
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            target_cpu_percentage: Target CPU utilization percentage (1-100)
            labels: Labels to apply to the HPA resource
        """
        self.name = name
        self.namespace = namespace
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.target_cpu_percentage = target_cpu_percentage
        self.labels = labels
        
        # Validate inputs
        self._validate()
    
    def _validate(self):
        """Validate all inputs."""
        # Validate name
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        
        # Validate namespace
        if not self.namespace or not isinstance(self.namespace, str):
            raise ValueError("namespace must be a non-empty string")
        
        # Validate min_replicas
        if not isinstance(self.min_replicas, int):
            raise ValueError("min_replicas must be an integer")
        if self.min_replicas < 1:
            raise ValueError(f"min_replicas must be >= 1, got {self.min_replicas}")
        
        # Validate max_replicas
        if not isinstance(self.max_replicas, int):
            raise ValueError("max_replicas must be an integer")
        if self.max_replicas < 1:
            raise ValueError(f"max_replicas must be >= 1, got {self.max_replicas}")
        
        # Validate min <= max
        if self.min_replicas > self.max_replicas:
            raise ValueError(
                f"min_replicas ({self.min_replicas}) cannot be greater than "
                f"max_replicas ({self.max_replicas})"
            )
        
        # Validate target_cpu_percentage
        if not isinstance(self.target_cpu_percentage, int):
            raise ValueError("target_cpu_percentage must be an integer")
        if self.target_cpu_percentage < 1 or self.target_cpu_percentage > 100:
            raise ValueError(
                f"target_cpu_percentage must be between 1 and 100, "
                f"got {self.target_cpu_percentage}"
            )
        
        # Validate labels
        if not isinstance(self.labels, dict):
            raise ValueError("labels must be a dictionary")
    
    def build(self) -> dict:
        """
        Build and return the HorizontalPodAutoscaler resource definition.
        
        Returns:
            Complete HPA resource as a dictionary
        """
        return {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f'{self.name}-hpa',
                'namespace': self.namespace,
                'labels': self.labels,
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': f'{self.name}-deployment',
                },
                'minReplicas': self.min_replicas,
                'maxReplicas': self.max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': self.target_cpu_percentage,
                            }
                        }
                    }
                ],
            }
        }