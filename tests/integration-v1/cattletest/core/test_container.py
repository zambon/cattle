import json

from cattle import ApiError
from common import *  # NOQA


def test_container_create_count(client, context):
    cs = client.create_container(imageUuid=context.image_uuid,
                                 count=3)

    assert len(cs) == 3

    for c in cs:
        c = client.wait_success(c)
        assert c.state == 'running'


def test_conatiner_simple_start(context):
    context.create_container()


def test_container_build(super_client, context, client):
    container = context.create_container(build={
        'dockerfile': 'test/Dockerfile',
        'remote': 'http://example.com',
        'rm': True,
    })

    assert container.build.dockerfile == 'test/Dockerfile'
    assert container.build.remote == 'http://example.com'
    assert container.build.rm

    container = super_client.reload(container)
    assert container.data.fields.build.dockerfile == 'test/Dockerfile'
    assert container.data.fields.build.remote == 'http://example.com'
    assert container.data.fields.build.tag == context.image_uuid
    assert container.data.fields.build.rm


def test_container_create_only(super_client, client, context):
    uuid = "sim:{}".format(random_num())
    container = super_client.create_container(accountId=context.project.id,
                                              imageUuid=uuid,
                                              name="test" + random_str(),
                                              startOnCreate=False)

    assert_fields(container, {
        "type": "container",
        "allocationState": "inactive",
        "state": "creating",
        "imageUuid": uuid,
        "firstRunning": None,
    })

    container = super_client.wait_success(container)

    assert_fields(container, {
        "type": "container",
        "allocationState": "inactive",
        "state": "stopped",
        "imageUuid": uuid,
    })

    container = super_client.reload(container)

    assert container.instanceTriggeredStop == 'stop'

    nics = container.nics()
    assert len(nics) == 1

    return client.reload(container)


def _assert_running(container):
    assert_fields(container, {
        "allocationState": "active",
        "state": "running",
        "startCount": NOT_NONE,
        "hostId": NOT_NONE,
        "firstRunning": NOT_NONE
    })

    instance_host_mappings = container.instanceHostMaps()
    assert len(instance_host_mappings) == 1

    assert_fields(instance_host_mappings[0], {
        "state": "active"
    })


def test_container_special_labels(client, context):
    uuid = "sim:{}".format(random_num())
    labels = {
        'io.rancher.container.display_name': 'from-label',
        'io.rancher.container.network': 'true',
    }
    container = client.create_container(accountId=context.project.id,
                                        networkMode='none',
                                        imageUuid=uuid,
                                        name="test" + random_str(),
                                        labels=labels,
                                        startOnCreate=False)
    container = client.wait_success(container)

    assert container.state == 'stopped'
    assert container.name == 'from-label'
    assert container.networkMode == 'managed'


def test_container_create_then_start(super_client, client, context):
    container = client.create_container(startOnCreate=False,
                                        imageUuid=context.image_uuid)
    container = client.wait_success(container)
    container = container.start()

    assert container.state == "starting"
    assert 'start' not in container
    assert 'stop' in container
    assert 'remove' not in container

    _assert_running(super_client.wait_success(container))


def test_container_first_running(client, context):
    c = client.create_container(imageUuid=context.image_uuid,
                                startOnCreate=False)
    c = client.wait_success(c)

    assert c.state == 'stopped'
    assert c.firstRunning is None

    c = client.wait_success(c.start())
    assert c.state == 'running'
    assert c.firstRunning is not None

    first = c.firstRunning

    c = client.wait_success(c.restart())
    assert c.state == 'running'
    assert c.firstRunning == first


def test_container_restart(client, super_client, context):
    container = context.create_container()

    _assert_running(super_client.reload(container))

    container = context.client.wait_success(container)
    container = container.restart()

    assert container.state == 'restarting'
    container = client.wait_success(container)
    _assert_running(super_client.reload(container))


def test_container_stop(client, super_client, context):
    container = context.create_container(name="test" + random_str())
    container = client.wait_success(container)

    assert_fields(container, {
        "state": "running"
    })

    container = container.stop()

    assert_fields(container, {
        "state": "stopping"
    })

    container = client.wait_success(container)

    assert_fields(super_client.reload(container), {
        "allocationState": "active",
        "state": "stopped"
    })

    container = super_client.reload(container)
    instance_host_mappings = container.instanceHostMaps()
    assert len(instance_host_mappings) == 1
    assert instance_host_mappings[0].state == 'inactive'


def _assert_removed(container):
    assert_removed_fields(container)
    return container


def _assert_error(container):
    assert container.state == "error"
    return container


def test_container_remove(client, super_client, context):
    container = context.create_container(name="test" + random_str())
    container = client.wait_success(container)
    container = client.wait_success(container.stop())

    assert container.state == "stopped"

    container = container.remove()

    assert container.state == "removing"

    container = client.wait_success(container)

    _assert_removed(super_client.reload(container))
    return container


def test_container_delete_while_running(client, super_client, context):
    container = context.create_container(name="test" + random_str())
    container = client.wait_success(container)
    assert container.state == 'running'

    container = client.delete(container)
    assert container.state == 'stopping'

    container = client.wait_success(container)
    _assert_removed(super_client.reload(container))
    return container


def test_start_stop(client, context):
    container = context.create_container(name="test" + random_str())

    container = client.wait_success(container)

    for _ in range(5):
        assert container.state == 'running'
        container = client.wait_success(container.stop())
        assert container.state == 'stopped'
        container = client.wait_success(container.start())
        assert container.state == 'running'


def test_container_primary_network_id(client, context):
    c = context.create_container()
    c = client.wait_success(c)

    assert c.networkMode == 'managed'
    assert c.primaryNetworkId is not None


def test_container_image_required(client):
    try:
        client.create_container()
        assert False
    except ApiError as e:
        assert e.error.status == 422
        assert e.error.code == 'MissingRequired'
        assert e.error.fieldName == 'imageUuid'


def test_container_compute_fail(super_client, context):
    data = {
        'compute.instance.activate::fail': True,
        'io.cattle.platform.process.instance.InstanceStart': {
            'computeTries': 1
        }
    }

    container = context.super_create_container_no_success(data=data)

    assert container.transitioning == 'error'
    assert container.transitioningMessage == \
        'Failing [compute.instance.activate]'

    _assert_error(super_client.reload(container))


def test_container_restart_policy(super_client, client):
    for c in [super_client, client]:
        restart_policy = c.schema.types['restartPolicy']
        assert len(restart_policy.resourceFields) == 2
        assert 'name' in restart_policy.resourceFields
        assert 'maximumRetryCount' in restart_policy.resourceFields
        container = c.schema.types['container']
        assert 'restartPolicy' == \
               container.resourceFields['restartPolicy'].type


def test_container_exec_on_stop(client, context):
    c = context.create_container()

    assert callable(c.execute)
    c = client.wait_success(c.stop())

    assert 'execute' not in c


def test_container_exec(context):
    c = context.create_container()

    assert callable(c.execute)

    resp = c.execute(command=['/bin/sh'])

    assert resp.url is not None
    assert resp.token is not None

    jwt = _get_jwt(resp.token)

    assert jwt['exec']['AttachStdin']
    assert jwt['exec']['AttachStdout']
    assert jwt['exec']['Tty']
    assert jwt['exec']['Cmd'] == ['/bin/sh']
    assert jwt['exec']['Container'] == c.externalId
    assert jwt['exp'] is not None

    resp = c.execute(command=['/bin/sh2', 'blah'], attachStdin=False,
                     attachStdout=False, tty=False)

    assert resp.url is not None
    assert resp.token is not None

    jwt = _get_jwt(resp.token)

    assert not jwt['exec']['AttachStdin']
    assert not jwt['exec']['AttachStdout']
    assert not jwt['exec']['Tty']
    assert jwt['exec']['Cmd'] == ['/bin/sh2', 'blah']

    context.delete(c)


def test_container_logs(context):
    c = context.create_container()

    assert callable(c.logs)

    resp = c.logs(follow=True, lines=300)

    assert resp.url is not None
    assert resp.token is not None

    jwt = _get_jwt(resp.token)

    assert jwt['logs']['Container'] == c.externalId
    assert jwt['logs']['Lines'] == 300
    assert jwt['logs']['Follow'] is True
    assert jwt['exp'] is not None

    resp = c.logs()

    assert resp.url is not None
    assert resp.token is not None

    jwt = _get_jwt(resp.token)

    assert jwt['logs']['Container'] == c.externalId
    assert jwt['logs']['Lines'] == 100
    assert jwt['logs']['Follow'] is True
    assert jwt['exp'] is not None

    context.delete(c)


def test_container_labels(client, context):
    labels = {'affinity': "container==B", '!affinity': "container==C"}
    container = context.create_container(name="test" + random_str(),
                                         labels=labels)
    container = client.wait_success(container)
    assert container.state == 'running'
    assert all(item in container.labels.items()
               for item in labels.items())


def _get_jwt(token):
    text = token.split('.')[1]
    missing_padding = 4 - len(text) % 4
    if missing_padding:
        text += '=' * missing_padding

    return json.loads(base64.b64decode(text))


def test_container_request_ip(super_client, client, context):
    for i in range(2):
        # Doing this twice essentially ensure that the IP gets freed the first
        # time
        container = client.create_container(imageUuid=context.image_uuid,
                                            startOnCreate=False)
        container = super_client.wait_success(container)
        assert container.state == 'stopped'
        container.data.fields['requestedIpAddress'] = '10.42.33.33'

        container = super_client.update(container, data=container.data)
        container = super_client.wait_success(container.start())

        assert container.primaryIpAddress == '10.42.33.33'

        # Try second time and should fail because it is used
        container2 = client.create_container(imageUuid=context.image_uuid,
                                             startOnCreate=False)
        container2 = super_client.wait_success(container2)
        assert container2.state == 'stopped'
        container2.data.fields['requestedIpAddress'] = '10.42.33.33'

        container2 = super_client.update(container2, data=container2.data)
        container2 = super_client.wait_success(container2.start())

        assert container2.primaryIpAddress != '10.42.33.33'

        # Release 1.1.1.1
        container = super_client.wait_success(super_client.delete(container))

        nics = container.nics()
        assert len(nics) == 0


def test_container_network_modes(context, super_client):
    c = context.create_container(networkMode=None)
    c = super_client.wait_success(c)
    assert c.state == 'running'
    assert len(c.nics()) == 0

    target = context.create_container(networkMode='bridge')
    target = super_client.wait_success(target)
    assert c.state == 'running'
    assert len(target.nics()) == 1

    for i in [('host', 'dockerHost'), ('none', 'dockerNone'),
              ('container', 'dockerContainer'), ('bridge', 'dockerBridge'),
              ('managed', 'network')]:
        args = {
            'networkMode': i[0]
        }
        if i[0] == 'container':
            args['networkContainerId'] = target.id

        c = context.create_container(**args)
        c = super_client.wait_success(c)
        assert c.state == 'running'
        assert len(c.nics()) == 1
        assert c.nics()[0].network().kind == i[1]


def test_container_resource_actions_json_state(context):
    c = context.create_container(startOnCreate=True)
    c.stop()
    c.logs()
    c = context.client.wait_success(c)
    c.logs()
    context.client.delete(c)
    c = context.client.wait_success(c)
    assert 'logs' not in c


def test_container_network_host_mode_w_dsn(context, super_client):
    labels = {'io.rancher.container.dns': "true"}
    c = context.create_container(networkMode='host', labels=labels)
    c = super_client.wait_success(c)
    assert c.state == 'running'
    assert len(c.nics()) == 1
    assert c.nics()[0].network().kind == 'dockerHost'


def test_container_request_ip_from_label(new_context):
    client = new_context.client
    labels = {
        'io.rancher.container.requested_ip': '10.42.42.42'
    }

    c = new_context.create_container(labels=labels)
    assert c.primaryIpAddress == '10.42.42.42'

    c = client.wait_success(client.delete(c))
    assert c.state == 'removed'

    c = new_context.create_container(labels=labels)
    assert c.primaryIpAddress == '10.42.42.42'

    c = new_context.create_container(labels=labels)
    assert c.primaryIpAddress != '10.42.42.42'
