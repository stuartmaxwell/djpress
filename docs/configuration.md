# Configuration

## DJ Press Settings

In your settings.py file, create a `DJPRESS_SETTINGS` dictionary. Here are some common settings:

```python
# DJPress settings
DJPRESS_SETTINGS = {
    "SITE_TITLE": "My Awesome Blog",
    "POST_PREFIX": "{{ year }}/{{ month }}",
}
```

There are lots more settings available. Please checks the docs or look at the source code:
[src/djpress/app_settings.py](https://github.com/stuartmaxwell/djpress/blob/main/src/djpress/app_settings.py)

## Themes

There are two themes included with DJ Press: "default" and "simple". They can be configured as follows:

```python
# DJPress settings
DJPRESS_SETTINGS = {
    "THEME": "simple",
}
```

To create, your own theme please read the [Theme documentation](themes.md)
