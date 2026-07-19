_DEFAULT_NAME = "OwOMIZU ON TOP"

_ACTIVITY_TYPES = {
    "playing": 0,
    "streaming": 1,
    "listening": 2,
    "watching": 3,
    "competing": 5,
}


def resolve_activity_type(name):
    if not isinstance(name, str):
        return 0
    return _ACTIVITY_TYPES.get(name.strip().lower(), 0)


def _clean(value):
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def build_activity_kwargs(cfg):
    if not isinstance(cfg, dict):
        cfg = {}

    name = _clean(cfg.get("text")) or _DEFAULT_NAME
    kwargs = {
        "name": name,
        "type": resolve_activity_type(cfg.get("activityType")),
    }

    app_id = None
    raw_id = cfg.get("applicationId")
    if raw_id is not None:
        try:
            app_id = int(raw_id)
        except (TypeError, ValueError):
            app_id = None

    if app_id is not None:
        kwargs["application_id"] = app_id

        assets = {}
        large = _clean(cfg.get("largeImage"))
        if large:
            assets["large_image"] = large
            large_text = _clean(cfg.get("largeText"))
            if large_text:
                assets["large_text"] = large_text

        small = _clean(cfg.get("smallImage"))
        if small:
            assets["small_image"] = small
            small_text = _clean(cfg.get("smallText"))
            if small_text:
                assets["small_text"] = small_text

        if assets:
            kwargs["assets"] = assets

    return kwargs
