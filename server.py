#!/usr/bin/env python3
"""
OrbStack MCP Server
Manage Docker containers, Linux VMs, and Kubernetes through MCP.
"""

import subprocess
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("orbstack-mcp")


# ── Helper ─────────────────────────────────────────────────────────


def run(cmd: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            error = result.stderr.strip()
            return (
                f"Error: {error}"
                if error
                else f"Command failed with code {result.returncode}"
            )
        return output if output else "Done."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error: {str(e)}"


# ── Docker Container Tools ─────────────────────────────────────────


@mcp.tool()
def docker_list_containers(all: bool = False) -> str:
    """List Docker containers. Set all=True to include stopped containers."""
    flags = "-a" if all else ""
    fmt = "table {{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"
    return run(f'docker ps {flags} --format "{fmt}"')


@mcp.tool()
def docker_run(
    image: str,
    name: Optional[str] = None,
    ports: Optional[list[str]] = None,
    env: Optional[list[str]] = None,
    volumes: Optional[list[str]] = None,
    detach: bool = True,
    extra_args: Optional[str] = None,
) -> str:
    """Create and start a new Docker container.

    Args:
        image: Docker image to run (e.g. 'nginx:latest')
        name: Container name
        ports: Port mappings (e.g. ['8080:80', '443:443'])
        env: Environment variables (e.g. ['KEY=value'])
        volumes: Volume mounts (e.g. ['/host:/container'])
        detach: Run in background (default: True)
        extra_args: Any additional docker run flags
    """
    cmd = "docker run"
    if detach:
        cmd += " -d"
    if name:
        cmd += f" --name {name}"
    if ports:
        for p in ports:
            cmd += f" -p {p}"
    if env:
        for e in env:
            cmd += f" -e {e}"
    if volumes:
        for v in volumes:
            cmd += f" -v {v}"
    if extra_args:
        cmd += f" {extra_args}"
    cmd += f" {image}"
    return run(cmd)


@mcp.tool()
def docker_stop(containers: list[str]) -> str:
    """Stop one or more running containers.

    Args:
        containers: Container names or IDs to stop
    """
    return run(f"docker stop {' '.join(containers)}")


@mcp.tool()
def docker_start(containers: list[str]) -> str:
    """Start one or more stopped containers.

    Args:
        containers: Container names or IDs to start
    """
    return run(f"docker start {' '.join(containers)}")


@mcp.tool()
def docker_restart(containers: list[str]) -> str:
    """Restart one or more containers.

    Args:
        containers: Container names or IDs to restart
    """
    return run(f"docker restart {' '.join(containers)}")


@mcp.tool()
def docker_rm(containers: list[str], force: bool = False, volumes: bool = False) -> str:
    """Remove one or more containers.

    Args:
        containers: Container names or IDs to remove
        force: Force removal of running containers
        volumes: Remove associated volumes
    """
    cmd = "docker rm"
    if force:
        cmd += " -f"
    if volumes:
        cmd += " -v"
    cmd += f" {' '.join(containers)}"
    return run(cmd)


@mcp.tool()
def docker_logs(container: str, tail: int = 100) -> str:
    """Fetch logs from a container.

    Args:
        container: Container name or ID
        tail: Number of lines from the end (default: 100)
    """
    return run(f"docker logs --tail {tail} {container}")


@mcp.tool()
def docker_exec(container: str, command: str) -> str:
    """Execute a command inside a running container.

    Args:
        container: Container name or ID
        command: Command to execute (e.g. 'ls -la /app')
    """
    return run(f"docker exec {container} {command}")


@mcp.tool()
def docker_inspect(container: str) -> str:
    """Return detailed JSON information about a container.

    Args:
        container: Container name or ID
    """
    return run(f"docker inspect {container}")


@mcp.tool()
def docker_stats(containers: Optional[list[str]] = None) -> str:
    """Show resource usage statistics for running containers.

    Args:
        containers: Specific container names/IDs (default: all running)
    """
    targets = " ".join(containers) if containers else ""
    return run(f"docker stats --no-stream {targets}")


# ── Docker Image Tools ─────────────────────────────────────────────


@mcp.tool()
def docker_images() -> str:
    """List all Docker images."""
    return run(
        "docker images --format 'table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}'"
    )


@mcp.tool()
def docker_pull(image: str) -> str:
    """Pull a Docker image from a registry.

    Args:
        image: Image to pull (e.g. 'nginx:latest')
    """
    return run(f"docker pull {image}")


@mcp.tool()
def docker_rmi(images: list[str], force: bool = False) -> str:
    """Remove one or more Docker images.

    Args:
        images: Image names or IDs to remove
        force: Force removal
    """
    cmd = "docker rmi"
    if force:
        cmd += " -f"
    cmd += f" {' '.join(images)}"
    return run(cmd)


# ── Docker Compose Tools ───────────────────────────────────────────


@mcp.tool()
def docker_compose_up(
    project_dir: str, detach: bool = True, services: Optional[list[str]] = None
) -> str:
    """Start services defined in a docker-compose file.

    Args:
        project_dir: Path to the directory containing docker-compose.yml
        detach: Run in background (default: True)
        services: Specific services to start
    """
    cmd = f"docker compose -f {project_dir}/docker-compose.yml up"
    if detach:
        cmd += " -d"
    if services:
        cmd += f" {' '.join(services)}"
    return run(cmd)


@mcp.tool()
def docker_compose_down(project_dir: str, volumes: bool = False) -> str:
    """Stop and remove services defined in a docker-compose file.

    Args:
        project_dir: Path to the directory containing docker-compose.yml
        volumes: Remove volumes too
    """
    cmd = f"docker compose -f {project_dir}/docker-compose.yml down"
    if volumes:
        cmd += " -v"
    return run(cmd)


@mcp.tool()
def docker_compose_ps(project_dir: str) -> str:
    """List containers for a compose project.

    Args:
        project_dir: Path to the directory containing docker-compose.yml
    """
    return run(f"docker compose -f {project_dir}/docker-compose.yml ps")


# ── Docker System Tools ────────────────────────────────────────────


@mcp.tool()
def docker_system_prune(all: bool = False, volumes: bool = False) -> str:
    """Remove unused Docker data (containers, images, networks, build cache).

    Args:
        all: Remove all unused images, not just dangling
        volumes: Also prune volumes
    """
    cmd = "docker system prune -f"
    if all:
        cmd += " -a"
    if volumes:
        cmd += " --volumes"
    return run(cmd)


@mcp.tool()
def docker_system_df() -> str:
    """Show Docker disk usage."""
    return run("docker system df")


# ── Docker Network Tools ───────────────────────────────────────────


@mcp.tool()
def docker_network_ls() -> str:
    """List Docker networks."""
    return run("docker network ls")


@mcp.tool()
def docker_network_create(name: str, driver: Optional[str] = None) -> str:
    """Create a Docker network.

    Args:
        name: Network name
        driver: Network driver (default: bridge)
    """
    cmd = "docker network create"
    if driver:
        cmd += f" -d {driver}"
    cmd += f" {name}"
    return run(cmd)


# ── Docker Volume Tools ────────────────────────────────────────────


@mcp.tool()
def docker_volume_ls() -> str:
    """List Docker volumes."""
    return run("docker volume ls")


@mcp.tool()
def docker_volume_create(name: str) -> str:
    """Create a Docker volume.

    Args:
        name: Volume name
    """
    return run(f"docker volume create {name}")


# ── OrbStack VM Tools ─────────────────────────────────────────────


@mcp.tool()
def orb_list() -> str:
    """List OrbStack Linux machines (VMs)."""
    return run("orb list")


@mcp.tool()
def orb_start(machine: str) -> str:
    """Start an OrbStack Linux machine.

    Args:
        machine: Machine name to start
    """
    result = run(f"orb start {machine}")
    return result if "Error" in result else f"Machine '{machine}' started."


@mcp.tool()
def orb_stop(machine: str) -> str:
    """Stop an OrbStack Linux machine.

    Args:
        machine: Machine name to stop
    """
    result = run(f"orb stop {machine}")
    return result if "Error" in result else f"Machine '{machine}' stopped."


@mcp.tool()
def orb_create(distro: str, name: Optional[str] = None) -> str:
    """Create a new OrbStack Linux machine.

    Args:
        distro: Linux distro (e.g. 'ubuntu', 'debian', 'fedora', 'arch')
        name: Custom machine name
    """
    cmd = f"orb create {distro}"
    if name:
        cmd += f" {name}"
    result = run(cmd)
    return result if "Error" in result else f"Machine created with distro '{distro}'."


@mcp.tool()
def orb_delete(machine: str) -> str:
    """Delete an OrbStack Linux machine.

    Args:
        machine: Machine name to delete
    """
    result = run(f"orb delete -f {machine}")
    return result if "Error" in result else f"Machine '{machine}' deleted."


@mcp.tool()
def orb_run(machine: str, command: str) -> str:
    """Run a command inside an OrbStack Linux machine.

    Args:
        machine: Machine name
        command: Command to run
    """
    return run(f"orb run -m {machine} -- {command}")


@mcp.tool()
def orb_info() -> str:
    """Get OrbStack system info and status."""
    status = run("orbctl status")
    docker_info = run(
        "docker info --format 'Server: {{.ServerVersion}} | Containers: {{.Containers}} | Images: {{.Images}}'"
    )
    return f"OrbStack Status:\n{status}\n\nDocker Info:\n{docker_info}"


# ── Kubernetes Tools ───────────────────────────────────────────────


@mcp.tool()
def kubectl_get(
    resource: str,
    namespace: Optional[str] = None,
    all_namespaces: bool = False,
) -> str:
    """Get Kubernetes resources (pods, services, deployments, etc.).

    Args:
        resource: Resource type (e.g. 'pods', 'services', 'deployments', 'nodes')
        namespace: Namespace (default: 'default')
        all_namespaces: Show resources across all namespaces
    """
    cmd = f"kubectl get {resource}"
    if all_namespaces:
        cmd += " -A"
    elif namespace:
        cmd += f" -n {namespace}"
    return run(cmd)


@mcp.tool()
def kubectl_describe(resource: str, name: str, namespace: Optional[str] = None) -> str:
    """Describe a Kubernetes resource in detail.

    Args:
        resource: Resource type (e.g. 'pod', 'service')
        name: Resource name
        namespace: Namespace
    """
    cmd = f"kubectl describe {resource} {name}"
    if namespace:
        cmd += f" -n {namespace}"
    return run(cmd)


@mcp.tool()
def kubectl_logs(
    pod: str,
    namespace: Optional[str] = None,
    container: Optional[str] = None,
    tail: Optional[int] = None,
) -> str:
    """Get logs from a Kubernetes pod.

    Args:
        pod: Pod name
        namespace: Namespace
        container: Specific container in the pod
        tail: Number of lines from the end
    """
    cmd = f"kubectl logs {pod}"
    if namespace:
        cmd += f" -n {namespace}"
    if container:
        cmd += f" -c {container}"
    if tail:
        cmd += f" --tail={tail}"
    return run(cmd)


@mcp.tool()
def kubectl_apply(file: str, namespace: Optional[str] = None) -> str:
    """Apply a Kubernetes manifest from a file path.

    Args:
        file: Path to the YAML/JSON manifest file
        namespace: Namespace
    """
    cmd = f"kubectl apply -f {file}"
    if namespace:
        cmd += f" -n {namespace}"
    return run(cmd)


# ── Run ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
