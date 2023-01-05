
up:
	sh scripts/devcontainer.sh up

down:
	sh scripts/devcontainer.sh down

dev:
	docker exec -it image-retrieval /bin/bash
