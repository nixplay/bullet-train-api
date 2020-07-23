from threading import Thread

from webhooks.webhooks import (
    call_environment_webhooks,
    WebhookEventType,
    WebhookType,
    call_organisation_webhooks,
    _call_webhooks,
)

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"


def trigger_feature_state_change_webhooks(instance):
    history_instance = instance.history.first()
    timestamp = (
        history_instance.history_date.strftime(date_format)
        if history_instance and history_instance.history_date
        else ""
    )

    changed_by = (
        str(history_instance.history_user)
        if history_instance and history_instance.history_user
        else ""
    )

    data = {
        "new_state": _get_feature_state_webhook_data(instance),
        "changed_by": changed_by,
        "timestamp": timestamp,
    }

    if history_instance.prev_record:
        data["previous_state"] = _get_feature_state_webhook_data(
            history_instance.prev_record.instance, previous=True
        )

    env_webhooks = list(instance.environment.webhooks.filter(enabled=True))
    org_webhooks = list(instance.environment.project.organisation.webhooks.filter(enabled=True))

    Thread(
        target=_call_webhooks,
        args=(env_webhooks, data, WebhookEventType.FLAG_UPDATED, WebhookType.ENVIRONMENT),
    ).start()

    Thread(
        target=_call_webhooks,
        args=(org_webhooks, data, WebhookEventType.FLAG_UPDATED, WebhookType.ORGANISATION),
    ).start()


def _get_feature_state_webhook_data(feature_state, previous=False):
    # TODO: fix circular imports and use serializers instead.
    feature = feature_state.feature
    feature_state_value = (
        feature_state.get_feature_state_value()
        if not previous
        else feature_state.previous_feature_state_value
    )
    identity_identifier = (
        feature_state.identity.identifier if feature_state.identity else None
    )

    data = {
        "feature": {
            "id": feature.id,
            "created_date": feature.created_date.strftime(date_format),
            "default_enabled": feature.default_enabled,
            "description": feature.description,
            "initial_value": feature.initial_value,
            "name": feature.name,
            "project": feature.project_id,
            "type": feature.type,
        },
        "environment": feature_state.environment_id,
        "identity": feature_state.identity_id,
        "identity_identifier": identity_identifier,
        "feature_segment": None,  # default to none, will be updated below if it exists
        "enabled": feature_state.enabled,
        "feature_state_value": feature_state_value,
    }

    if feature_state.feature_segment:
        feature_segment = feature_state.feature_segment
        data["feature_segment"] = {
            "segment": {
                "id": feature_segment.segment.id,
                "name": feature_segment.segment.name,
                "description": feature_segment.segment.description,
            },
            "priority": feature_segment.priority,
            "enabled": feature_segment.enabled,
            "value": feature_segment.get_value(),
        }

    return data
