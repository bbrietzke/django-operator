"""
DeploymentBuilder - Creates Kubernetes Deployment resources for Django applications.
"""


class DeploymentBuilder:
    """
    Builds a Kubernetes Deployment resource for a Django application.
    
    The builder validates all inputs and returns a complete Deployment
    definition ready to be applied to the cluster.
    """
    
    def __init__(self, name: str, namespace: str, image: str, port: int,
                 resources: dict, labels: dict, pod_labels: dict, 
                 min_replicas: int, env: list = None):
        """
        Initialize the DeploymentBuilder.
        
        Args:
            name: Name of the DjangoApp (will create {name}-deployment)
            namespace: Kubernetes namespace
            image: Container image (e.g., 'registry/app:tag')
            port: Port the Django application listens on
            resources: Resource requests and limits dict
            labels: Labels to apply to the Deployment resource
            pod_labels: Labels to apply to pods (used by Service selector)
            min_replicas: Initial number of replicas (from autoscale.min)
            env: Optional list of environment variable dicts with 'name' and 'value'
        """
        self.name = name
        self.namespace = namespace
        self.image = image
        self.port = port
        self.resources = resources
        self.labels = labels
        self.pod_labels = pod_labels
        self.min_replicas = min_replicas
        self.env = env or []
        
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
        
        # Validate image
        if not self.image or not isinstance(self.image, str):
            raise ValueError("image must be a non-empty string")
        
        # Validate port
        if not isinstance(self.port, int):
            raise ValueError("port must be an integer")
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"port must be between 1 and 65535, got {self.port}")
        
        # Validate resources
        if not isinstance(self.resources, dict):
            raise ValueError("resources must be a dictionary")
        if 'requests' not in self.resources:
            raise ValueError("resources must contain 'requests' key")
        if not isinstance(self.resources['requests'], dict):
            raise ValueError("resources.requests must be a dictionary")
        if 'cpu' not in self.resources['requests']:
            raise ValueError("resources.requests must contain 'cpu'")
        if 'memory' not in self.resources['requests']:
            raise ValueError("resources.requests must contain 'memory'")
        
        # Validate limits if present
        if 'limits' in self.resources:
            if not isinstance(self.resources['limits'], dict):
                raise ValueError("resources.limits must be a dictionary")
        
        # Validate labels
        if not isinstance(self.labels, dict):
            raise ValueError("labels must be a dictionary")
        if not isinstance(self.pod_labels, dict):
            raise ValueError("pod_labels must be a dictionary")
        
        # Validate min_replicas
        if not isinstance(self.min_replicas, int):
            raise ValueError("min_replicas must be an integer")
        if self.min_replicas < 1:
            raise ValueError(f"min_replicas must be >= 1, got {self.min_replicas}")
        
        # Validate env if provided
        if self.env is not None:
            if not isinstance(self.env, list):
                raise ValueError("env must be a list")
            for item in self.env:
                if not isinstance(item, dict):
                    raise ValueError("each env item must be a dictionary")
                if 'name' not in item or 'value' not in item:
                    raise ValueError("each env item must have 'name' and 'value' keys")
    
    def build(self) -> dict:
        """
        Build and return the Deployment resource definition.
        
        Returns:
            Complete Deployment resource as a dictionary
        """
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f'{self.name}-deployment',
                'namespace': self.namespace,
                'labels': self.labels,
            },
            'spec': {
                'replicas': self.min_replicas,
                'selector': {
                    'matchLabels': self.pod_labels,
                },
                'template': {
                    'metadata': {
                        'labels': self.pod_labels,
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'django',
                                'image': self.image,
                                'ports': [
                                    {
                                        'containerPort': self.port,
                                        'name': 'http',
                                        'protocol': 'TCP',
                                    }
                                ],
                                'env': self.env,
                                'resources': self.resources,
                            }
                        ],
                    }
                }
            }
        }