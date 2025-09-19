# Ubuntu Base Image Preparation

The Universal Coding Tool expects a hardened Ubuntu 22.04 image that ships with
rootless Docker support and VMware guest tools. Follow the steps below from a
macOS host using VMware Fusion or Workstation.

1. **Download Ubuntu 22.04 ISO** from Canonical and create a new VM using the
   “Custom” wizard. Allocate at least 2 vCPUs, 4 GB RAM and a 40 GB disk.
2. **Install Ubuntu** using the minimal profile. Set the hostname to
   `uct-sandbox` and create an administrative user named `sandbox-admin`.
3. Once installation is complete:
   - Update packages: `sudo apt update && sudo apt upgrade -y`
   - Install utilities: `sudo apt install -y cloud-init cloud-guest-utils \
     openssh-server python3-pip jq unzip`
   - Install VMware tools: `sudo apt install -y open-vm-tools`
4. **Configure rootless Docker** for the `sandbox` user:
   ```bash
   sudo adduser --disabled-password --gecos "" sandbox
   sudo -u sandbox /usr/bin/dockerd-rootless-setuptool.sh install
   sudo loginctl enable-linger sandbox
   ```
5. **Enable cloud-init NoCloud datasource:**
   ```bash
   sudo mkdir -p /var/lib/cloud/seed/nocloud
   sudo tee /etc/cloud/cloud.cfg.d/99-nocloud.cfg <<'CFG'
   datasource_list: [ NoCloud ]
   datasource:
     NoCloud:
       seedfrom: /var/lib/cloud/seed/nocloud/
   CFG
   ```
6. **Create snapshot directory** inside the guest that will receive job payloads:
   ```bash
   sudo mkdir -p /var/lib/uct
   sudo chown sandbox:sandbox /var/lib/uct
   ```
7. Shut down the VM and create a VMware snapshot named `CLEAN_BASE`. Future
   jobs will revert to this snapshot before execution.
8. Export the VMX path (e.g. `/Users/<you>/Documents/Virtual Machines/UCT.vmwarevm/UCT.vmx`) and update `.env`.

Refer to `docs/OPERATIONS.md` for lifecycle management guidance.
