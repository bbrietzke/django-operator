"""
ServiceBuilder - Creates Kubernetes Service resources.
"""


class ServiceBuilder:
    """
    Builds a Kubernetes Service resource to expose the Django application.
    
    The Service provides a stable endpoint for accessing the Deployment's pods.
    """
    
    def __init__(self, name: str, namespace: str, port: int, 
                 labels: dict, pod_labels: dict):
        """
        Initialize the ServiceBuilder.
        
        Args:
            name: Name of the DjangoApp (will create {name}-service)
            namespace: Kubernetes namespace
            port: Target port the Django application listens on
            labels: Labels to apply to the Service resource
            pod_labels: Selector labels to match pods created by the Deployment
        """
        self.name = name
        self.namespace = namespace
        self.port = port
        self.labels = labels
        self.pod_labels = pod_labels
        
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
        
        # Validate port
        if not isinstance(self.port, int):
            raise ValueError("port must be an integer")
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"port must be between 1 and 65535, got {self.port}")
        
        # Validate labels
        if not isinstance(self.labels, dict):
            raise ValueError("labels must be a dictionary")
        if not isinstance(self.pod_labels, dict):
            raise ValueError("pod_labels must be a dictionary")
    
    def build(self) -> dict:
        """
        Build and return the Service resource definition.
        
        Returns:
            Complete Service resource as a dictionary
        """
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f'{self.name}-service',
                'namespace': self.namespace,
                'labels': self.labels,
            },
            'spec': {
                'type': 'ClusterIP',
                'selector': self.pod_labels,
                'ports': [
                    {
                        'name': 'http',
                        'protocol': 'TCP',
                        'port': 80,
                        'targetPort': self.port,
                    }
                ],
            }
        }