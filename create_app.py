from api.app import create_app

# TODO: Allow for environment to be specified when running create app 
# eg `python create_app.py --env developement`
# if --env == development: config = api.config.DevConfig

app = create_app('api.config.DevConfig')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
