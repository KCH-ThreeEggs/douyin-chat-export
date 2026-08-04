# Architecture

The desktop executable hosts the existing FastAPI application in a background thread and renders the control panel in a native PyWebView window. Frozen subprocess invocations are routed back into the same executable as extraction workers.
