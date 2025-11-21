"""
IngressBuilder - Creates Kubernetes Ingress resources.
"""


class IngressBuilder:
    """
    Builds a Kubernetes Ingress resource to expose the Service externally.
    
    The Ingress routes external HTTP(S) traffic to the Service.
    """
    
    def __init__(self, name: str, namespace: str, ingress_class: str, 
                 host: str, labels: dict):
        """
        Initialize the IngressBuilder.
        
        Args:
            name: Name of the DjangoApp (will create {name}-ingress, route to {name}-service)
            namespace: Kubernetes namespace
            ingress_class: Ingress class name (e.g., 'nginx', 'traefik')
            host: Hostname for the ingress (e.g., 'myapp.example.com')
            labels: Labels to apply to the Ingress resource
        """
        self.name = name
        self.namespace = namespace
        self.ingress_class = ingress_class
        self.host = host
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
        
        # Validate ingress_class
        if not self.ingress_class or not isinstance(self.ingress_class, str):
            raise ValueError("ingress_class must be a non-empty string")
        
        # Validate host
        if not self.host or not isinstance(self.host, str):
            raise ValueError("host must be a non-empty string")
        
        # Validate labels
        if not isinstance(self.labels, dict):
            raise ValueError("labels must be a dictionary")
    
    def build(self) -> dict:
        """
        Build and return the Ingress resource definition.
        
        Returns:
            Complete Ingress resource as a dictionary
        """
        return {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': f'{self.name}-ingress',
                'namespace': self.namespace,
                'labels': self.labels,
            },
            'spec': {
                'ingressClassName': self.ingress_class,
                'rules': [
                    {
                        'host': self.host,
                        'http': {
                            'paths': [
                                {
                                    'path': '/',
                                    'pathType': 'Prefix',
                                    'backend': {
                                        'service': {
                                            'name': f'{self.name}-service',
                                            'port': {
                                                'number': 80,
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }