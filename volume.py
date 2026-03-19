def create_volume(volume_requests):
    commands = []

    for req in volume_requests:
        count = req["count"]
        size = req["size"]
        pool = req["pool"]

        for i in range(1, count + 1):
            name = f"{pool}_vol{i}"
            cmd = f"create volume size {size} pool {pool} name {name}"
            commands.append(cmd)

    return "\n".join(commands)


def expand_volume(volume_name, size):
    return f"expand volume {volume_name} size {size}"