from blinker import signal


signal_navigation_event = signal("signal_navigation_event")
signal_state_update = signal("signal_state_update")
signal_clear_input_field_event = signal("signal_clear_input_field_event")
signal_default_event = signal("signal_default_event")


__all__ = ["signal_navigation_event", "signal_state_update", "signal_clear_input_field_event", "signal_default_event"]
