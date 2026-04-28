import docker
import os
import uuid
from loguru import logger

class SandboxManager:
    """Manages isolated execution of the Claude CLI in Docker containers."""
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client. Is Docker running? {e}")
            self.client = None

    def create_sandbox(self, project_path: str) -> str:
        """Creates a new sandbox container and returns its ID."""
        if not self.client:
            raise RuntimeError("Docker client not available.")
        
        container_name = f"claude-sandbox-{uuid.uuid4().hex[:8]}"
        try:
            container = self.client.containers.run(
                "advanced-claude-sandbox:latest",
                command="tail -f /dev/null", # Keep alive
                name=container_name,
                detach=True,
                volumes={os.path.abspath(project_path): {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace",
                network_mode="none", # Strict egress isolation
                mem_limit="512m",
                cpus=1.0,
            )
            logger.info(f"Sandbox created: {container_name}")
            return container.id
        except Exception as e:
            logger.error(f"Error creating sandbox: {e}")
            raise

    def execute_command(self, container_id: str, command: str) -> tuple[int, str]:
        """Executes a command inside the sandbox."""
        if not self.client:
            raise RuntimeError("Docker client not available.")
            
        try:
            container = self.client.containers.get(container_id)
            logger.debug(f"Executing in {container_id[:8]}: {command}")
            exit_code, output = container.exec_run(command)
            return exit_code, output.decode('utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Failed to execute command in sandbox: {e}")
            raise

    def auto_fix_loop(self, container_id: str, test_command: str, max_iterations: int = 3) -> bool:
        """
        Runs a test command. If it fails, it sends the error to the local LLM proxy,
        gets a fix (mocked here), applies it, and re-tests until success or max_iterations.
        """
        logger.info(f"Starting Auto-Fix Loop for command: {test_command}")
        
        for i in range(max_iterations):
            exit_code, output = self.execute_command(container_id, test_command)
            
            if exit_code == 0:
                logger.success(f"Auto-Fix Loop successful on iteration {i+1}!")
                return True
                
            logger.warning(f"Iteration {i+1} failed. Output: {output.strip()}")
            logger.info("Sending error to local LLM for autonomous fix...")
            
            # In a real scenario, this would call the proxy LLM to generate a sed/patch command.
            # For scaffolding, we simulate applying a fix.
            fix_command = "echo 'Fixing bugs automatically...'"
            self.execute_command(container_id, fix_command)
            
        logger.error(f"Auto-Fix Loop failed after {max_iterations} iterations.")
        return False

    def destroy_sandbox(self, container_id: str):
        """Kills and removes the sandbox container."""
        if not self.client:
            return
            
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Sandbox destroyed: {container_id[:8]}")
        except docker.errors.NotFound:
            pass
        except Exception as e:
            logger.error(f"Failed to destroy sandbox {container_id[:8]}: {e}")
