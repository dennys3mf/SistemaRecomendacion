# FRONT END
	Paso 1
	docker pull bhukzers050702/tiktok-frontend:tagname
	Paso 2
	docker images
	Paso 3
	docker run it -p 8080:80 --name api 4b139et3241

# BACK END
	Paso 1
	docker pull bhukzers050702/api-tiktok:tagname
	Paso 2
	docker images
	Paso 3
	docker run it -p 8080:80 --name front 2b1394efc41b

En cloud: > Copiamos la URL de la api generada por playwithdocker y la pegamos en nuestro front-end
![image](https://github.com/dennys3mf/SistemaRecomendacion/assets/70309655/8af3190b-048a-42ec-bf5a-97b9af1b981b)
![image](https://github.com/dennys3mf/SistemaRecomendacion/assets/70309655/068ae71e-1f6a-4039-a6c9-0a539b3f7bec)
![image](https://github.com/dennys3mf/SistemaRecomendacion/assets/70309655/99d0ee48-e597-429c-9c98-507bb2617280)
![image](https://github.com/dennys3mf/SistemaRecomendacion/assets/70309655/1a74dfd2-0647-4375-875d-99453f3bee18)
![image](https://github.com/dennys3mf/SistemaRecomendacion/assets/70309655/f9543ff7-1f8a-4f58-952f-506bed6fc831)

En  local, ejecutamos el siguiente comando:
## docker-compose up --build
