"""
Test script for builder classes.

This script tests each builder independently to ensure they:
1. Validate inputs correctly
2. Generate proper Kubernetes resource definitions
3. Handle edge cases appropriately
"""

import json
from builders import DeploymentBuilder, HPABuilder, ServiceBuilder, IngressBuilder
from helpers import get_common_labels, get_pod_labels


def test_deployment_builder():
    """Test the DeploymentBuilder."""
    print("Testing DeploymentBuilder...")
    
    name = "test-app"
    namespace = "default"
    image = "myregistry/django-app:v1.0"
    port = 8000
    resources = {
        'requests': {
            'cpu': '100m',
            'memory': '128Mi'
        },
        'limits': {
            'cpu': '500m',
            'memory': '512Mi'
        }
    }
    labels = get_common_labels(name)
    pod_labels = get_pod_labels(name)
    min_replicas = 2
    env = [
        {'name': 'DEBUG', 'value': 'false'},
        {'name': 'DJANGO_SETTINGS_MODULE', 'value': 'myapp.settings'}
    ]
    
    try:
        builder = DeploymentBuilder(
            name=name,
            namespace=namespace,
            image=image,
            port=port,
            resources=resources,
            labels=labels,
            pod_labels=pod_labels,
            min_replicas=min_replicas,
            env=env
        )
        deployment = builder.build()
        
        # Validate structure
        assert deployment['kind'] == 'Deployment'
        assert deployment['metadata']['name'] == 'test-app-deployment'
        assert deployment['spec']['replicas'] == 2
        assert deployment['spec']['template']['spec']['containers'][0]['image'] == image
        
        print("✓ DeploymentBuilder passed!")
        return True
    except Exception as e:
        print(f"✗ DeploymentBuilder failed: {e}")
        return False


def test_hpa_builder():
    """Test the HPABuilder."""
    print("\nTesting HPABuilder...")
    
    name = "test-app"
    namespace = "default"
    min_replicas = 2
    max_replicas = 10
    target_cpu = 70
    labels = get_common_labels(name)
    
    try:
        builder = HPABuilder(
            name=name,
            namespace=namespace,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            target_cpu_percentage=target_cpu,
            labels=labels
        )
        hpa = builder.build()
        
        # Validate structure
        assert hpa['kind'] == 'HorizontalPodAutoscaler'
        assert hpa['metadata']['name'] == 'test-app-hpa'
        assert hpa['spec']['minReplicas'] == 2
        assert hpa['spec']['maxReplicas'] == 10
        assert hpa['spec']['scaleTargetRef']['name'] == 'test-app-deployment'
        
        print("✓ HPABuilder passed!")
        return True
    except Exception as e:
        print(f"✗ HPABuilder failed: {e}")
        return False


def test_service_builder():
    """Test the ServiceBuilder."""
    print("\nTesting ServiceBuilder...")
    
    name = "test-app"
    namespace = "default"
    port = 8000
    labels = get_common_labels(name)
    pod_labels = get_pod_labels(name)
    
    try:
        builder = ServiceBuilder(
            name=name,
            namespace=namespace,
            port=port,
            labels=labels,
            pod_labels=pod_labels
        )
        service = builder.build()
        
        # Validate structure
        assert service['kind'] == 'Service'
        assert service['metadata']['name'] == 'test-app-service'
        assert service['spec']['type'] == 'ClusterIP'
        assert service['spec']['ports'][0]['targetPort'] == 8000
        
        print("✓ ServiceBuilder passed!")
        return True
    except Exception as e:
        print(f"✗ ServiceBuilder failed: {e}")
        return False


def test_ingress_builder():
    """Test the IngressBuilder."""
    print("\nTesting IngressBuilder...")
    
    name = "test-app"
    namespace = "default"
    ingress_class = "nginx"
    host = "test-app.example.com"
    labels = get_common_labels(name)
    
    try:
        builder = IngressBuilder(
            name=name,
            namespace=namespace,
            ingress_class=ingress_class,
            host=host,
            labels=labels
        )
        ingress = builder.build()
        
        # Validate structure
        assert ingress['kind'] == 'Ingress'
        assert ingress['metadata']['name'] == 'test-app-ingress'
        assert ingress['spec']['ingressClassName'] == 'nginx'
        assert ingress['spec']['rules'][0]['host'] == 'test-app.example.com'
        assert ingress['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] == 'test-app-service'
        
        print("✓ IngressBuilder passed!")
        return True
    except Exception as e:
        print(f"✗ IngressBuilder failed: {e}")
        return False


def test_validation():
    """Test that validation works correctly."""
    print("\nTesting validation...")
    
    # Test invalid port
    try:
        builder = DeploymentBuilder(
            name="test",
            namespace="default",
            image="test:v1",
            port=99999,  # Invalid!
            resources={'requests': {'cpu': '100m', 'memory': '128Mi'}},
            labels={},
            pod_labels={},
            min_replicas=1
        )
        print("✗ Validation failed to catch invalid port")
        return False
    except ValueError as e:
        print(f"✓ Correctly caught invalid port: {e}")
    
    # Test min > max
    try:
        builder = HPABuilder(
            name="test",
            namespace="default",
            min_replicas=10,
            max_replicas=5,  # Invalid!
            target_cpu_percentage=70,
            labels={}
        )
        print("✗ Validation failed to catch min > max")
        return False
    except ValueError as e:
        print(f"✓ Correctly caught min > max: {e}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Builder Tests")
    print("=" * 60)
    
    results = []
    results.append(test_deployment_builder())
    results.append(test_hpa_builder())
    results.append(test_service_builder())
    results.append(test_ingress_builder())
    results.append(test_validation())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)


if __name__ == '__main__':
    main()