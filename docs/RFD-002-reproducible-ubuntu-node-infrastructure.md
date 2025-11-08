# RFD-002: Reproducible Ubuntu-Node Infrastructure via Infrastructure-as-Code

## Metadata

- **Status:** 🟡 Proposed (Awaiting Discussion)
- **Date:** 2025-11-08
- **Author:** Community Contributor
- **Decision Makers:** Project Team
- **Impacts:** Development workflow, disaster recovery, contributor onboarding, maintenance burden
- **Related Documents:**
  - `docs/ubuntu-node-setup.md` (current manual setup documentation)
  - `docs/DEVELOPMENT_WORKFLOW.md` (two-machine workflow)
  - `docs/self-hosted-runner-setup.md` (CI/CD runner configuration)
  - `.devcontainer/devcontainer.json` (Codespace infrastructure - already reproducible)

---

## Executive Summary

**Problem:** The ubuntu-node is critical infrastructure for this project (firmware flashing, Home Assistant hosting, CI/CD runner), but its setup is **undocumented as code**. The current `ubuntu-node-setup.md` describes manual procedures, but doesn't provide a reproducible, versioned, automated way to provision a new node.

**Proposal:** Evaluate and adopt an infrastructure-as-code (IaC) approach to define the ubuntu-node environment, making it reproducible, version-controlled, and easily maintainable. Consider tools like **Ansible**, **Nix/NixOS**, **Docker Compose**, or a hybrid approach.

**Benefits:**
- ✅ **Disaster Recovery**: Quickly rebuild node if hardware fails
- ✅ **Contributor Onboarding**: New contributors can provision their own ubuntu-node
- ✅ **Version Control**: Track infrastructure changes alongside code
- ✅ **Consistency**: Eliminate "works on my machine" issues
- ✅ **Documentation**: Infrastructure becomes self-documenting code

**This RFD is exploratory** - it presents options and tradeoffs for discussion, not a final decision.

---

## Context

### Current State: Manual Ubuntu-Node Setup

The ubuntu-node is a critical component with multiple responsibilities:

1. **Physical Hardware Access**:
   - USB connection to M5Stack ESP32 device
   - Only location where firmware can be flashed via USB

2. **Network Services**:
   - Home Assistant (Docker container) at 192.168.0.148:8123
   - Cloudflare Tunnel for external access
   - SSH access for remote development

3. **Development Environment**:
   - ESPHome Python virtual environment
   - Git repository clone
   - Secrets management (source of truth for `secrets.yaml` and `.env.local`)

4. **CI/CD Infrastructure**:
   - GitHub Actions self-hosted runner
   - E2E test execution environment

**Problem: Setup is Manual and Undocumented**

`docs/ubuntu-node-setup.md` provides extensive documentation (1093 lines), but:
- ❌ **No automation**: All setup steps are manual copy-paste commands
- ❌ **No versioning**: Package versions not tracked (ESPHome, Python, Docker)
- ❌ **No reproducibility**: Cannot guarantee identical environment on new hardware
- ❌ **No validation**: No tests to verify setup is correct
- ❌ **Knowledge silos**: Configuration knowledge lives in documentation, not code
- ❌ **Drift risk**: Manual changes over time can deviate from documentation

**Contrast: Codespace Infrastructure is Already Reproducible**

The GitHub Codespace environment uses:
- `Dockerfile` for base image
- `devcontainer.json` for configuration
- `postCreateCommand` for automated setup
- Version-controlled dependencies

**Why not do the same for ubuntu-node?**

---

## Problem Statement

**As a contributor**, I want to:
1. Quickly provision a new ubuntu-node if hardware fails or I want to contribute
2. Understand exactly what software and versions are required
3. Be confident my node matches the "reference" configuration
4. Track infrastructure changes in git alongside code changes

**As a maintainer**, I want to:
1. Reduce time spent troubleshooting "my ubuntu-node is different" issues
2. Enable disaster recovery without manual reconstruction
3. Document infrastructure as code, not prose
4. Make onboarding contributors easier

**Current barriers:**
- New contributor must manually execute ~100 commands from `ubuntu-node-setup.md`
- No way to verify setup is correct except by trial-and-error (flashing firmware)
- Secrets management is manual and error-prone
- System updates or changes require manual documentation updates

---

## Requirements

Any infrastructure-as-code solution should meet these requirements:

### Functional Requirements

1. **Provision Core Services**:
   - Home Assistant (Docker container)
   - Cloudflare Tunnel (systemd service)
   - SSH server with authorized keys

2. **Development Environment**:
   - Python 3.12.3 (or specified version)
   - ESPHome 2025.10.4 (or specified version)
   - PlatformIO for native tests
   - Git repository clone

3. **USB/Hardware Access**:
   - Appropriate user groups (dialout, docker)
   - USB device permissions
   - Serial port access (/dev/ttyACM0)

4. **Secrets Management**:
   - Secure handling of WiFi credentials (secrets.yaml)
   - Secure handling of Home Assistant tokens (.env.local)
   - Cloudflare tunnel credentials
   - GitHub runner token

5. **Helper Scripts**:
   - `~/sync-and-flash.sh`
   - `~/flash-firmware.sh`
   - `~/WORKFLOW-README.md`

### Non-Functional Requirements

1. **Idempotent**: Re-running provisioning should be safe
2. **Fast**: Initial setup should complete in < 15 minutes
3. **Auditable**: Infrastructure changes tracked in git
4. **Portable**: Works on different Ubuntu 24.04 LTS hardware
5. **Documented**: Clear README for running provisioning
6. **Testable**: Verification tests to confirm setup is correct

---

## Options Considered

### Option 1: Ansible Playbooks (Declarative Configuration Management)

**What it is:**
- YAML-based declarative configuration management
- Industry-standard tool for server provisioning
- Agentless (runs over SSH)

**Implementation Approach:**

```yaml
# ansible/playbook.yml
---
- name: Provision Ubuntu Home Assistant Node
  hosts: ubuntu-node
  become: yes
  vars:
    python_version: "3.12.3"
    esphome_version: "2025.10.4"
    homeassistant_config_path: "/opt/homeassistant/config"

  tasks:
    - name: Install system packages
      apt:
        name:
          - docker.io
          - docker-compose
          - python3
          - python3-pip
          - python3-venv
          - git
        state: present
        update_cache: yes

    - name: Create user groups
      user:
        name: "{{ ansible_user }}"
        groups: docker,dialout
        append: yes

    - name: Deploy Home Assistant container
      docker_container:
        name: homeassistant
        image: homeassistant/home-assistant:latest
        state: started
        restart_policy: unless-stopped
        ports:
          - "8123:8123"
        volumes:
          - "{{ homeassistant_config_path }}:/config"

    - name: Create ESPHome virtual environment
      pip:
        name: esphome=={{ esphome_version }}
        virtualenv: /home/{{ ansible_user }}/esphome-venv
        virtualenv_command: python3 -m venv

    - name: Clone repository
      git:
        repo: https://github.com/your-org/bed-presence-sensor.git
        dest: /home/{{ ansible_user }}/bed-presence-sensor
        version: main

    # ... more tasks for Cloudflare, helper scripts, etc.
```

**Directory Structure:**
```
ansible/
├── playbook.yml           # Main provisioning playbook
├── inventory/
│   └── hosts.yml          # Node definitions
├── roles/
│   ├── homeassistant/     # HA-specific tasks
│   ├── esphome/           # ESPHome environment
│   ├── cloudflare/        # Tunnel setup
│   └── github-runner/     # Self-hosted runner
├── group_vars/
│   └── all.yml            # Common variables
└── README.md              # Usage instructions
```

**Pros:**
- ✅ **Industry standard**: Well-documented, large community
- ✅ **Declarative**: Describe desired state, not steps
- ✅ **Idempotent**: Re-running is safe (no duplicate changes)
- ✅ **Modular**: Roles can be reused and tested independently
- ✅ **Agentless**: No software installed on ubuntu-node beyond SSH
- ✅ **Secrets management**: Ansible Vault for encrypted secrets
- ✅ **Cross-platform**: Works on any Ubuntu/Debian system
- ✅ **Testing**: Can use Molecule for testing playbooks

**Cons:**
- ❌ **Learning curve**: YAML syntax, Ansible concepts (tasks, roles, handlers)
- ❌ **Dependencies**: Requires Ansible installed on control machine (Codespace or laptop)
- ❌ **SSH requirement**: Needs SSH access to target node
- ❌ **Not atomic**: Partial failures can leave system in intermediate state
- ❌ **Imperative aspects**: Some tasks still feel procedural
- ❌ **Slow for iterative testing**: Re-running playbook can be slow

**Secrets Management:**
```yaml
# ansible/group_vars/all.yml (encrypted with ansible-vault)
wifi_ssid: "TP-Link_BECC"
wifi_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...encrypted...
ha_token: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...encrypted...
```

**Usage:**
```bash
# Initial provision
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml

# Re-provision after changes
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml

# Verify setup
ansible-playbook -i ansible/inventory/hosts.yml ansible/verify.yml
```

---

### Option 2: Nix/NixOS (Declarative Functional Configuration)

**What it is:**
- Purely functional package manager and OS (NixOS)
- Declarative configuration in Nix language
- Atomic upgrades and rollbacks
- Reproducible builds

**Implementation Approach (NixOS):**

```nix
# configuration.nix
{ config, pkgs, ... }:

{
  # System packages
  environment.systemPackages = with pkgs; [
    git
    python312
    esphome
    platformio
  ];

  # Docker
  virtualisation.docker = {
    enable = true;
    autoPrune.enable = true;
  };

  # Home Assistant container
  virtualisation.oci-containers.containers.homeassistant = {
    image = "homeassistant/home-assistant:latest";
    ports = [ "8123:8123" ];
    volumes = [ "/opt/homeassistant/config:/config" ];
    autoStart = true;
  };

  # Cloudflare tunnel
  services.cloudflared = {
    enable = true;
    tunnels = {
      "my-tunnel" = {
        credentialsFile = "/etc/cloudflared/credentials.json";
        ingress = {
          "your-domain.com" = "http://localhost:8123";
          "ssh.your-domain.com" = "ssh://localhost:22";
        };
        default = "http_status:404";
      };
    };
  };

  # User configuration
  users.users.ryan = {
    isNormalUser = true;
    extraGroups = [ "wheel" "docker" "dialout" ];
  };

  # System state version
  system.stateVersion = "24.05";
}
```

**Pros:**
- ✅ **True reproducibility**: Bit-for-bit identical environments
- ✅ **Atomic rollbacks**: Instantly revert to previous configuration
- ✅ **Declarative**: Entire system in one file
- ✅ **Garbage collection**: Automatic cleanup of unused packages
- ✅ **Isolated environments**: Nix shells for project-specific dependencies
- ✅ **No dependency hell**: Packages don't conflict
- ✅ **Versioning**: Pin exact versions of all dependencies
- ✅ **Dev environments**: Can use Nix for Codespace too (consistency)

**Cons:**
- ❌ **STEEP learning curve**: Nix language is unfamiliar
- ❌ **Requires NixOS**: Would need to reinstall ubuntu-node as NixOS (major change)
- ❌ **Smaller community**: Less common than Ansible/Docker
- ❌ **Documentation gaps**: Fewer examples for niche use cases
- ❌ **Disk usage**: Nix store can grow large over time
- ❌ **Build times**: First build can be slow
- ❌ **Breaking change**: Existing ubuntu-node would need full wipe

**Alternative: Nix on Ubuntu (non-NixOS):**

```bash
# Install Nix on Ubuntu (non-invasive)
curl -L https://nixos.org/nix/install | sh

# Define environment in shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    esphome
    platformio
    git
  ];

  shellHook = ''
    export ESPHOME_VERSION="2025.10.4"
    echo "ESPHome development environment loaded"
  '';
}

# Enter environment
nix-shell
```

**Pros of Nix-on-Ubuntu:**
- ✅ No OS reinstall required
- ✅ Can coexist with apt packages
- ✅ Project-specific environments

**Cons of Nix-on-Ubuntu:**
- ❌ Doesn't manage system services (still need Docker, systemd)
- ❌ Hybrid approach (part Nix, part manual)

---

### Option 3: Docker Compose + Bootstrap Script (Container-First Approach)

**What it is:**
- Run all services in Docker containers
- Minimal host configuration via bootstrap script
- Services defined in `docker-compose.yml`

**Implementation Approach:**

```yaml
# docker-compose.yml (at ubuntu-node)
version: '3.8'

services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    container_name: homeassistant
    restart: unless-stopped
    network_mode: host
    volumes:
      - /opt/homeassistant/config:/config
      - /etc/localtime:/etc/localtime:ro

  esphome:
    image: esphome/esphome:latest
    container_name: esphome
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./esphome:/config
      - /etc/localtime:/etc/localtime:ro
    devices:
      - /dev/ttyACM0:/dev/ttyACM0  # USB device passthrough

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel run
    volumes:
      - /etc/cloudflared:/etc/cloudflared:ro
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}

  github-runner:
    image: myoung34/github-runner:latest
    container_name: github-runner
    restart: unless-stopped
    environment:
      - REPO_URL=https://github.com/your-org/bed-presence-sensor
      - RUNNER_TOKEN=${GITHUB_RUNNER_TOKEN}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./bed-presence-sensor:/workspace
```

```bash
# bootstrap.sh - Run on fresh Ubuntu 24.04 install
#!/bin/bash
set -euo pipefail

echo "Installing Docker..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git

echo "Adding user to docker group..."
sudo usermod -aG docker $USER

echo "Cloning repository..."
cd ~
git clone https://github.com/your-org/bed-presence-sensor.git

echo "Starting services..."
cd ~/bed-presence-sensor
docker-compose up -d

echo "Setup complete! Log out and back in for group changes to take effect."
```

**Pros:**
- ✅ **Simple**: Minimal host configuration needed
- ✅ **Portable**: Containers run anywhere Docker runs
- ✅ **Isolated**: Services don't conflict with host packages
- ✅ **Fast**: Docker Compose startup is quick
- ✅ **Familiar**: Many developers know Docker
- ✅ **Versioned**: Service versions in docker-compose.yml
- ✅ **Easy testing**: Can test locally on any machine

**Cons:**
- ❌ **USB passthrough complexity**: Docker USB device mapping can be finicky
- ❌ **Network mode: host**: Needed for HA discovery, but less isolated
- ❌ **Not a full solution**: Still need host-level setup (user groups, SSH, secrets)
- ❌ **Container overhead**: More resource usage than native
- ❌ **ESPHome limitations**: Flashing firmware from container can be problematic
- ❌ **GitHub runner in Docker**: Can have Docker-in-Docker issues

**Hybrid Approach: Docker Compose + Ansible**

Combine Docker for services, Ansible for host-level config:
- Ansible handles: user setup, SSH, udev rules, helper scripts
- Docker Compose handles: Home Assistant, Cloudflare, optional services

---

### Option 4: Terraform + Cloud-Init (Cloud-Native Approach)

**What it is:**
- Use Terraform to provision infrastructure
- Cloud-init for initial VM/server setup
- Suitable if running ubuntu-node on cloud VPS or local hypervisor

**Implementation Approach:**

```hcl
# terraform/main.tf
resource "proxmox_vm_qemu" "ubuntu_node" {
  name        = "ubuntu-home-assistant-node"
  target_node = "proxmox-host"

  clone = "ubuntu-24.04-template"

  cores  = 4
  memory = 4096

  # Cloud-init configuration
  cicustom = "user=local:snippets/user-data.yml"

  # Network
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  # USB device passthrough (M5Stack)
  usb {
    host = "1a86:55d4"  # M5Stack USB vendor:product
    usb3 = true
  }
}
```

```yaml
# cloud-init/user-data.yml
#cloud-config
users:
  - name: ryan
    groups: sudo,docker,dialout
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL

packages:
  - docker.io
  - docker-compose
  - git
  - python3
  - python3-pip

runcmd:
  - git clone https://github.com/your-org/bed-presence-sensor.git /home/ryan/bed-presence-sensor
  - python3 -m venv /home/ryan/esphome-venv
  - /home/ryan/esphome-venv/bin/pip install esphome==2025.10.4
  - docker run -d --name homeassistant --restart unless-stopped -p 8123:8123 -v /opt/homeassistant/config:/config homeassistant/home-assistant:latest
```

**Pros:**
- ✅ **Infrastructure-as-code**: Entire VM defined in Terraform
- ✅ **Cloud-portable**: Works with AWS, GCP, Azure, Proxmox, etc.
- ✅ **Immutable infrastructure**: Destroy and recreate nodes easily
- ✅ **Version controlled**: VM config tracked in git
- ✅ **Automated provisioning**: One command to create entire stack

**Cons:**
- ❌ **Requires hypervisor**: Not useful if ubuntu-node is bare metal
- ❌ **Overkill**: Too heavy if not already using Terraform/cloud
- ❌ **USB passthrough complexity**: VM USB mapping can be unreliable
- ❌ **Not applicable to current setup**: Ubuntu-node is likely bare metal N100

**Verdict:** Only viable if migrating ubuntu-node to VM/cloud infrastructure.

---

### Option 5: Bash Script + Makefile (Minimalist Approach)

**What it is:**
- Single comprehensive bash script to automate setup
- Makefile for common operations
- Git-tracked, executable documentation

**Implementation Approach:**

```bash
# setup-ubuntu-node.sh
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ESPHOME_VERSION="2025.10.4"
HA_CONFIG_DIR="/opt/homeassistant/config"

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }
error() { log "ERROR: $*" >&2; exit 1; }

# 1. System packages
log "Installing system packages..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose python3 python3-pip python3-venv git curl

# 2. User groups
log "Adding user to groups..."
sudo usermod -aG docker,dialout "$USER"

# 3. Home Assistant
log "Setting up Home Assistant..."
sudo mkdir -p "$HA_CONFIG_DIR"
docker run -d \
  --name homeassistant \
  --restart unless-stopped \
  -p 8123:8123 \
  -v "$HA_CONFIG_DIR:/config" \
  homeassistant/home-assistant:latest

# 4. ESPHome environment
log "Creating ESPHome virtual environment..."
python3 -m venv ~/esphome-venv
~/esphome-venv/bin/pip install esphome==$ESPHOME_VERSION platformio

# 5. Clone repository
log "Cloning repository..."
if [ ! -d ~/bed-presence-sensor ]; then
  git clone https://github.com/your-org/bed-presence-sensor.git ~/bed-presence-sensor
fi

# 6. Helper scripts
log "Creating helper scripts..."
cat > ~/sync-and-flash.sh <<'EOF'
#!/bin/bash
set -e
cd ~/bed-presence-sensor
git pull origin main
cd esphome
source ~/esphome-venv/bin/activate
esphome run bed-presence-detector.yaml --device /dev/ttyACM0
EOF
chmod +x ~/sync-and-flash.sh

# 7. Verification
log "Verifying setup..."
command -v docker >/dev/null || error "Docker not installed"
docker ps | grep -q homeassistant || error "Home Assistant not running"
[ -d ~/esphome-venv ] || error "ESPHome venv not created"

log "Setup complete! Log out and back in for group changes."
```

```makefile
# Makefile
.PHONY: help setup verify clean

help:
	@echo "Ubuntu-node management commands:"
	@echo "  make setup   - Initial setup of ubuntu-node"
	@echo "  make verify  - Verify setup is correct"
	@echo "  make clean   - Remove installed components"

setup:
	./setup-ubuntu-node.sh

verify:
	@echo "Verifying Docker..."
	@docker ps | grep homeassistant
	@echo "Verifying ESPHome..."
	@source ~/esphome-venv/bin/activate && esphome version
	@echo "Verifying USB device..."
	@ls -la /dev/ttyACM* || echo "Warning: No USB device found"
	@echo "All checks passed!"

clean:
	docker stop homeassistant || true
	docker rm homeassistant || true
	rm -rf ~/esphome-venv
	@echo "Cleaned up. Repository clone kept."
```

**Pros:**
- ✅ **Simple**: Just bash, no new tools to learn
- ✅ **Fast**: Runs quickly, no framework overhead
- ✅ **Transparent**: Easy to read and understand
- ✅ **No dependencies**: Works on any Linux system
- ✅ **Easy to debug**: Step through with `bash -x`
- ✅ **Incremental**: Can run parts of script manually

**Cons:**
- ❌ **Not idempotent**: Re-running can cause issues (duplicate installs)
- ❌ **Imperative**: Describes steps, not desired state
- ❌ **No rollback**: Manual undo if something breaks
- ❌ **Error handling**: Bash error handling is primitive
- ❌ **Testing difficulty**: Hard to test without running on real system
- ❌ **Maintenance burden**: Logic scattered across bash scripts

---

## Comparison Matrix

| Criterion | Ansible | Nix/NixOS | Docker Compose | Terraform | Bash Script |
|-----------|---------|-----------|----------------|-----------|-------------|
| **Learning Curve** | Medium | Steep | Low | Medium | Minimal |
| **Reproducibility** | High | Perfect | High | High | Medium |
| **Idempotency** | Yes | Yes | Partial | Yes | No |
| **Secrets Management** | Ansible Vault | sops-nix | .env files | Vault | Manual |
| **Rollback Support** | No | Yes (atomic) | Docker only | Yes (infra) | No |
| **Testing** | Molecule | VM/container | Easy | Easy | Manual |
| **Community Support** | Excellent | Good | Excellent | Excellent | N/A |
| **Maintenance Effort** | Low | Medium | Low | Medium | High |
| **Invasiveness** | Low (SSH) | High (OS) | Low (containers) | Medium (VM) | Low (script) |
| **Current Setup Impact** | Minimal | Full rebuild | Minimal | Full rebuild | Minimal |
| **Best For** | Multi-host | Full control | Services | Cloud infra | Simple setups |

---

## Recommended Approach: Hybrid Ansible + Docker Compose

**Rationale:**

After evaluating all options, a **hybrid approach combining Ansible for host configuration and Docker Compose for services** provides the best balance of:
- Reproducibility (Ansible's declarative tasks)
- Simplicity (Docker for services)
- Maintainability (well-documented tools)
- Non-invasiveness (no OS reinstall required)

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│           Ubuntu 24.04 LTS (bare metal)              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Ansible Playbook (Host Configuration)      │    │
│  │  • User groups (docker, dialout)           │    │
│  │  • System packages (git, python3)          │    │
│  │  • SSH authorized keys                     │    │
│  │  • Helper scripts                          │    │
│  │  • Secrets (encrypted with Ansible Vault)  │    │
│  └────────────────────────────────────────────┘    │
│                        │                            │
│                        ▼                            │
│  ┌────────────────────────────────────────────┐    │
│  │ Docker Compose (Services)                   │    │
│  │  • Home Assistant container                │    │
│  │  • Cloudflare Tunnel container             │    │
│  │  • (Optional) GitHub runner container      │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Native Installations                        │    │
│  │  • ESPHome venv (for USB flashing)         │    │
│  │  • PlatformIO (for native tests)           │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Why not pure Docker?**
- ESPHome flashing via USB is more reliable native
- GitHub runner in Docker has Docker-in-Docker complexity
- Some tasks (user groups, SSH) are better done at host level

**Why not pure Ansible?**
- Home Assistant updates easier with Docker (`docker pull`)
- Service isolation without managing systemd units
- Easier to test services locally

**Implementation Proposal:**

```
infrastructure/
├── README.md                  # Setup instructions
├── ansible/
│   ├── playbook.yml           # Main playbook
│   ├── inventory/
│   │   └── hosts.yml          # Node definition
│   ├── roles/
│   │   ├── common/            # Base system setup
│   │   ├── docker/            # Docker installation
│   │   ├── esphome/           # ESPHome venv
│   │   └── helpers/           # Helper scripts
│   └── group_vars/
│       └── all.yml            # Variables
├── docker-compose.yml         # Service definitions
├── .env.example               # Docker env template
└── verify.sh                  # Post-setup verification
```

**Usage:**

```bash
# One-time setup (from Codespace or laptop)
cd infrastructure
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml

# Verification
ssh ubuntu-node "docker ps"  # Should show homeassistant
ssh ubuntu-node "~/sync-and-flash.sh --help"  # Should work
```

---

## Migration Path

**Phase 1: Documentation and Planning** (1-2 weeks)
1. Create `infrastructure/` directory structure
2. Write initial Ansible playbook for one role (e.g., `common`)
3. Test on throwaway VM or Docker container
4. Document in `infrastructure/README.md`

**Phase 2: Iterative Implementation** (2-4 weeks)
1. Implement remaining Ansible roles
2. Convert Home Assistant setup to Docker Compose
3. Add verification script
4. Test end-to-end on spare hardware (if available)

**Phase 3: Validation** (1 week)
1. Run playbook against existing ubuntu-node (should be no-op or minimal changes)
2. Capture current state vs. desired state diff
3. Document any manual steps still required

**Phase 4: Documentation Update** (1 week)
1. Update `docs/ubuntu-node-setup.md` to reference IaC approach
2. Create `docs/disaster-recovery.md` guide
3. Add "Contributing: Infrastructure Changes" section

**Phase 5: Optional - Test Full Rebuild**
1. Provision new VM or spare hardware
2. Run playbook from scratch
3. Validate firmware flashing works
4. Compare to production ubuntu-node

---

## Open Questions for Discussion

1. **Secrets Management**:
   - Use Ansible Vault? External secrets manager (1Password, Bitwarden)? Git-crypt?
   - How to handle initial bootstrap (chicken-egg: need secrets to provision, need provision to store secrets)?

2. **Scope**:
   - Should this also manage Codespace environment consistency? (currently uses Dockerfile)
   - Should we provision local development machines (contributor laptops)?

3. **Testing**:
   - How to test Ansible playbook changes without breaking production ubuntu-node?
   - Should we set up a CI pipeline for testing infrastructure changes?

4. **Governance**:
   - Who maintains the infrastructure code?
   - How to handle breaking changes (e.g., upgrading ESPHome version)?

5. **Alternatives**:
   - Should we consider cloud-hosted ubuntu-node (e.g., Raspberry Pi in cloud) for better accessibility?
   - Would a dev container for ESPHome eliminate need for ubuntu-node? (USB-over-network?)

6. **Nix Interest**:
   - Is the team interested in exploring Nix despite learning curve?
   - Could start with `nix-shell` for ESPHome environment only?

---

## Success Criteria

This RFD will be considered successful if we achieve:

- [ ] New contributor can provision ubuntu-node in < 30 minutes
- [ ] Infrastructure changes are versioned in git
- [ ] `make verify` command confirms setup is correct
- [ ] Documentation (`ubuntu-node-setup.md`) references IaC approach
- [ ] Secrets are encrypted and safely stored
- [ ] Disaster recovery time < 2 hours (from hardware failure to working node)

---

## Next Steps

1. **Gather Feedback**: Discuss this RFD in project channels
2. **Vote on Approach**: Decide between Ansible, Nix, Docker, or other
3. **Prototype**: Create proof-of-concept for chosen approach
4. **Iterate**: Refine based on testing and feedback
5. **Document**: Update project docs to reflect new workflow
6. **Roll Out**: Apply to production ubuntu-node

---

## References

### External Documentation

- **Ansible**: https://docs.ansible.com/
- **Ansible Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Nix/NixOS**: https://nixos.org/
- **Nix Pills (Learning Nix)**: https://nixos.org/guides/nix-pills/
- **Docker Compose**: https://docs.docker.com/compose/
- **Home Assistant Docker**: https://www.home-assistant.io/installation/linux#docker-compose
- **ESPHome**: https://esphome.io/

### Related Projects

- **home-assistant/supervised-installer**: https://github.com/home-assistant/supervised-installer (Docker-based HA)
- **awesome-home-assistant**: https://www.awesome-ha.com/ (IaC examples)
- **nixos-hardware**: https://github.com/NixOS/nixos-hardware (NixOS hardware configs)

### Code References (This Project)

- `docs/ubuntu-node-setup.md` - Current manual setup (1093 lines)
- `docs/DEVELOPMENT_WORKFLOW.md` - Two-machine workflow
- `.devcontainer/devcontainer.json` - Codespace IaC example
- `scripts/deploy_esphome.sh` - Deployment automation
- `docker-compose.yml` - N/A (doesn't exist yet - would be created)

---

## Approval & History

- **2025-11-08**: RFD-002 created, awaiting discussion
- **Status**: 🟡 Proposed (needs team feedback)

**Next Review**: After community discussion (target: 2 weeks)

---

## Appendix: Example Secrets Management (Ansible Vault)

**Creating encrypted secrets:**

```bash
# Create encrypted file
ansible-vault create ansible/group_vars/secrets.yml

# Edit encrypted file
ansible-vault edit ansible/group_vars/secrets.yml

# Content (unencrypted view):
---
wifi_ssid: "TP-Link_BECC"
wifi_password: "actual_password_here"
ha_token: "eyJ0eXAiOiJKV1..."
cloudflare_tunnel_token: "eyJhIjoiN..."
github_runner_token: "A7xK9..."
```

**Using in playbook:**

```yaml
# ansible/roles/esphome/tasks/main.yml
- name: Create secrets.yaml for ESPHome
  template:
    src: secrets.yaml.j2
    dest: "{{ repo_path }}/esphome/secrets.yaml"
    mode: '0600'

# templates/secrets.yaml.j2
wifi_ssid: "{{ wifi_ssid }}"
wifi_password: "{{ wifi_password }}"
ap_password: "{{ ap_password }}"
```

**Running with vault:**

```bash
ansible-playbook -i inventory/hosts.yml playbook.yml --ask-vault-pass
# or
ansible-playbook -i inventory/hosts.yml playbook.yml --vault-password-file ~/.vault_pass
```

---

**End of RFD-002**
