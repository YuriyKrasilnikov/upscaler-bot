docker build -t upscaler-bot -f .docker\dockerfile .\ --progress=plain

# test
docker run --rm -it -p 8080:8080 --entrypoint bash upscaler-bot

flask --app main_flask --debug run --no-debugger --no-reload --host=0.0.0.0 --port=8080

export API_TOKEN={API_TOKEN}

# save yandex
docker tag upscaler-bot cr.yandex/{}/upscaler-bot

docker push cr.yandex/{}/upscaler-bot
