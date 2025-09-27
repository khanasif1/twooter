#************************************
#******Build and deploy at scale ****
#************************************
#***********LOGIN :SHAISTA***********
# Build Image
.\deploy.ps1 -Action build -ImageTag "shaista"

#Push to docker
 .\deploy.ps1 -Action push -ImageTag "shaista"

 # Deploy to Azure Container Instances Login :shaista
.\deploy.ps1 -Action deploy-azure -ImageTag "shaista"

 #***********LOGIN :smart_citizen***********
 # Build Image
.\deploy-basic.ps1 build smart-citizen

#Push to docker
 .\deploy-basic.ps1 push smart-citizen

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen

 #***********LOGIN :smart_citizen_au***********
 # Build Image
.\deploy-basic.ps1 build smart-citizen-au
#Push to docker
 .\deploy-basic.ps1 push smart-citizen-au

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-au


  #***********LOGIN :smart_citizen_nz***********
 # Build Image
.\deploy-basic.ps1 build smart-citizen-nz
#Push to docker
 .\deploy-basic.ps1 push smart-citizen-nz

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-nz


#***********LOGIN :smart_citizen_in***********
 # Build Image
.\deploy-basic.ps1 build smart-citizen-in
#Push to docker
 .\deploy-basic.ps1 push smart-citizen-in

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-in


#Deploy 20 instance

1..7 | ForEach-Object { .\deploy.ps1 -Action deploy-azure -ImageTag "shaista" }
