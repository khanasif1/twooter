#************************************
#******Build and deploy at scale ****
#************************************
#***********LOGIN :SHAISTA***********
# Build Image
.\deploy.ps1 build shaista

#Push to docker
 .\deploy.ps1 push shaista

 # Deploy to Azure Container Instances Login :shaista
 .\ACI-Deployment.ps1 deploy shaista
 
 #***********LOGIN :smart_citizen***********
 # Build Image
.\deploy.ps1 build smart-citizen

#Push to docker
 .\deploy.ps1 push smart-citizen

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen

 #***********LOGIN :smart_citizen_au***********
 # Build Image
.\deploy.ps1 build smart-citizen-au
#Push to docker
 .\deploy.ps1 push smart-citizen-au

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-au


  #***********LOGIN :smart_citizen_nz***********
 # Build Image
.\deploy.ps1 build smart-citizen-nz
#Push to docker
 .\deploy.ps1 push smart-citizen-nz

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-nz


#***********LOGIN :smart_citizen_in***********
 # Build Image
.\deploy.ps1 build smart-citizen-in
#Push to docker
 .\deploy.ps1 push smart-citizen-in

 # Deploy to Azure Container Instances Login :smart_citizen
 .\ACI-Deployment.ps1 deploy smart-citizen-in

