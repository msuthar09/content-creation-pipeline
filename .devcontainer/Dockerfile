# Reference: https://github.com/devcontainers/images/blob/main/src/typescript-node/.devcontainer/Dockerfile

FROM mcr.microsoft.com/devcontainers/universal:2-focal

###############################################################################

# # Install Python
# RUN apt-get update \
#     # Install Python
#     && apt-get install -y --no-install-recommends python3.11 python3-pip \
#     \
#     # Cleanup
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Install Node.Js
# RUN apt-get update \
#     && apt-get install -y software-properties-common curl npm \
#     && npm install -g n \
#     && n lts

# # Install .NET SDK
# # Reference: https://github.com/dotnet/dotnet-docker/blob/main/documentation/scenarios/installing-dotnet.md
# RUN export DEBIAN_FRONTEND=noninteractive \
#     && apt-get update \
#     # Install prerequisites
#     && apt-get install -y --no-install-recommends \
#        wget \
#        ca-certificates \
#     \
#     # Install Microsoft package feed
#     && wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
#     && dpkg -i packages-microsoft-prod.deb \
#     && rm packages-microsoft-prod.deb \
#     \
#     # Install .NET
#     && apt-get update \
#     && apt-get install -y --no-install-recommends \
#         dotnet-runtime-6.0 \
#     \
#     # Cleanup
#     && rm -rf /var/lib/apt/lists/*

###############################################################################

# Install tslint, typescript
# ARG NODE_MODULES="eslint tslint-to-eslint-config typescript yarn yo generator-code"
# RUN umask 0002 \
#     && npm install -g ${NODE_MODULES} \
#     && npm cache clean --force > /dev/null 2>&1

###############################################################################

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment if you want to install an additional version of node using nvm
# ARG EXTRA_NODE_VERSION=10
# RUN su node -c "source /usr/local/share/nvm/nvm.sh && nvm install ${EXTRA_NODE_VERSION}"

# [Optional] Uncomment if you want to install more global node packages
# RUN su node -c "npm install -g <your-package-list -here>"
