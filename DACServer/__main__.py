if __name__ == "__main__":
    from quart import Quart
    from . import DACBlueprint
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    cfg = Config()
    
    cfg.backlog = 1000
    cfg.max_app_queue_size = 1000
    print(f'backlog {cfg.backlog}')
    print(f'max app size {cfg.max_app_queue_size}')
    print(f'workers {cfg.workers}')
    app = Quart("DAC Unit", )
    app.register_blueprint(DACBlueprint, url_prefix='/')
    # cfg.bind = ['0.0.0.0:{}'.format(sys.argv.pop(0) if len(sys.argv) > 0 else 9216)]
    
    asyncio.run(
        serve(
            app, 
            cfg
        )
    )