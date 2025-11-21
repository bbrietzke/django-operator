"""
Django App Operator - Main handler file

This module contains the Kopf event handlers for DjangoApp resources.
"""

import kopf
from kubernetes import client, config
from builders import DeploymentBuilder, HPABuilder, ServiceBuilder, IngressBuilder
from helpers import get_common_labels, get_pod_labels


# Load Kubernetes configuration
# This works both in-cluster and with local kubeconfig
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()


@kopf.on.create('faultycloud.io', 'v1alpha1', 'djangoapps')
def create_djangoapp(spec, name, namespace, logger, **kwargs):
    """
    Handler for when a DjangoApp resource is created.
    
    Creates the following resources in order:
    1. Deployment
    2. HorizontalPodAutoscaler
    3. Service
    4. Ingress
    """
    logger.info(f"Creating DjangoApp: {name} in namespace: {namespace}")
    
    # Extract data from spec
    deployment_spec = spec['deployment']
    ingress_spec = spec['ingress']
    autoscale_spec = spec['autoscale']
    env_vars = spec.get('env', [])
    
    # Generate labels
    labels = get_common_labels(name)
    pod_labels = get_pod_labels(name)
    
    logger.info(f"Extracted spec - image: {deployment_spec['image']}, "
                f"port: {deployment_spec['port']}, "
                f"min: {autoscale_spec.get('min', 1)}, "
                f"max: {autoscale_spec.get('max', 1)}")
    
    # Initialize Kubernetes API clients
    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    autoscaling_api = client.AutoscalingV2Api()
    networking_api = client.NetworkingV1Api()
    
    try:
        # 1. Create Deployment
        logger.info("Creating Deployment...")
        deployment_builder = DeploymentBuilder(
            name=name,
            namespace=namespace,
            image=deployment_spec['image'],
            port=deployment_spec['port'],
            resources=deployment_spec['resources'],
            labels=labels,
            pod_labels=pod_labels,
            min_replicas=autoscale_spec.get('min', 1),
            env=env_vars
        )
        deployment_body = deployment_builder.build()
        kopf.adopt(deployment_body)
        apps_api.create_namespaced_deployment(
            namespace=namespace,
            body=deployment_body
        )
        logger.info(f"✓ Created Deployment: {name}-deployment")
        
        # 2. Create HorizontalPodAutoscaler
        logger.info("Creating HorizontalPodAutoscaler...")
        hpa_builder = HPABuilder(
            name=name,
            namespace=namespace,
            min_replicas=autoscale_spec.get('min', 1),
            max_replicas=autoscale_spec.get('max', 1),
            target_cpu_percentage=autoscale_spec['targetCPUUtilizationPercentage'],
            labels=labels
        )
        hpa_body = hpa_builder.build()
        kopf.adopt(hpa_body)
        autoscaling_api.create_namespaced_horizontal_pod_autoscaler(
            namespace=namespace,
            body=hpa_body
        )
        logger.info(f"✓ Created HPA: {name}-hpa")
        
        # 3. Create Service
        logger.info("Creating Service...")
        service_builder = ServiceBuilder(
            name=name,
            namespace=namespace,
            port=deployment_spec['port'],
            labels=labels,
            pod_labels=pod_labels
        )
        service_body = service_builder.build()
        kopf.adopt(service_body)
        core_api.create_namespaced_service(
            namespace=namespace,
            body=service_body
        )
        logger.info(f"✓ Created Service: {name}-service")
        
        # 4. Create Ingress
        logger.info("Creating Ingress...")
        ingress_builder = IngressBuilder(
            name=name,
            namespace=namespace,
            ingress_class=ingress_spec['ingressClassName'],
            host=ingress_spec['host'],
            labels=labels
        )
        ingress_body = ingress_builder.build()
        kopf.adopt(ingress_body)
        networking_api.create_namespaced_ingress(
            namespace=namespace,
            body=ingress_body
        )
        logger.info(f"✓ Created Ingress: {name}-ingress")
        
        logger.info(f"✓ Successfully created all resources for DjangoApp: {name}")
        
        # Return a status message that will be stored
        return {
            'deployment': f'{name}-deployment',
            'service': f'{name}-service',
            'hpa': f'{name}-hpa',
            'ingress': f'{name}-ingress',
            'message': 'All resources created successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to create resources: {e}")
        raise kopf.PermanentError(f"Failed to create resources: {e}")


@kopf.on.update('faultycloud.io', 'v1alpha1', 'djangoapps')
def update_djangoapp(spec, name, namespace, logger, **kwargs):
    """
    Handler for when a DjangoApp resource is updated.
    
    Updates the child resources to match the new spec.
    """
    logger.info(f"Updating DjangoApp: {name} in namespace: {namespace}")
    
    # Extract data from spec
    deployment_spec = spec['deployment']
    ingress_spec = spec['ingress']
    autoscale_spec = spec['autoscale']
    env_vars = spec.get('env', [])
    
    # Generate labels
    labels = get_common_labels(name)
    pod_labels = get_pod_labels(name)
    
    # Initialize Kubernetes API clients
    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    autoscaling_api = client.AutoscalingV2Api()
    networking_api = client.NetworkingV1Api()
    
    try:
        # Update Deployment
        logger.info("Updating Deployment...")
        deployment_builder = DeploymentBuilder(
            name=name,
            namespace=namespace,
            image=deployment_spec['image'],
            port=deployment_spec['port'],
            resources=deployment_spec['resources'],
            labels=labels,
            pod_labels=pod_labels,
            min_replicas=autoscale_spec.get('min', 1),
            env=env_vars
        )
        deployment_body = deployment_builder.build()
        kopf.adopt(deployment_body)
        apps_api.patch_namespaced_deployment(
            name=f'{name}-deployment',
            namespace=namespace,
            body=deployment_body
        )
        logger.info(f"✓ Updated Deployment: {name}-deployment")
        
        # Update HPA
        logger.info("Updating HPA...")
        hpa_builder = HPABuilder(
            name=name,
            namespace=namespace,
            min_replicas=autoscale_spec.get('min', 1),
            max_replicas=autoscale_spec.get('max', 1),
            target_cpu_percentage=autoscale_spec['targetCPUUtilizationPercentage'],
            labels=labels
        )
        hpa_body = hpa_builder.build()
        kopf.adopt(hpa_body)
        autoscaling_api.patch_namespaced_horizontal_pod_autoscaler(
            name=f'{name}-hpa',
            namespace=namespace,
            body=hpa_body
        )
        logger.info(f"✓ Updated HPA: {name}-hpa")
        
        # Update Service
        logger.info("Updating Service...")
        service_builder = ServiceBuilder(
            name=name,
            namespace=namespace,
            port=deployment_spec['port'],
            labels=labels,
            pod_labels=pod_labels
        )
        service_body = service_builder.build()
        kopf.adopt(service_body)
        core_api.patch_namespaced_service(
            name=f'{name}-service',
            namespace=namespace,
            body=service_body
        )
        logger.info(f"✓ Updated Service: {name}-service")
        
        # Update Ingress
        logger.info("Updating Ingress...")
        ingress_builder = IngressBuilder(
            name=name,
            namespace=namespace,
            ingress_class=ingress_spec['ingressClassName'],
            host=ingress_spec['host'],
            labels=labels
        )
        ingress_body = ingress_builder.build()
        kopf.adopt(ingress_body)
        networking_api.patch_namespaced_ingress(
            name=f'{name}-ingress',
            namespace=namespace,
            body=ingress_body
        )
        logger.info(f"✓ Updated Ingress: {name}-ingress")
        
        logger.info(f"✓ Successfully updated all resources for DjangoApp: {name}")
        
        return {'message': 'All resources updated successfully'}
        
    except Exception as e:
        logger.error(f"Failed to update resources: {e}")
        raise kopf.PermanentError(f"Failed to update resources: {e}")


@kopf.on.delete('faultycloud.io', 'v1alpha1', 'djangoapps')
def delete_djangoapp(spec, name, namespace, logger, **kwargs):
    """
    Handler for when a DjangoApp resource is deleted.
    
    Note: With owner references set via kopf.adopt(), 
    child resources are automatically cleaned up by Kubernetes.
    """
    logger.info(f"Deleting DjangoApp: {name} in namespace: {namespace}")
    logger.info("Child resources will be automatically deleted via owner references")
    
    return {'message': 'DjangoApp deleted, child resources will be cleaned up automatically'}
