import hou
import ConfigParser


def get_rop_nodes_list(out_node):
    rop_nodes = []
    cache_nodes = []
    render_nodes = {"rop_nodes": [], "cache_nodes": []}
    for child in out_node.children():
        # node is set to current frame, so we skip it
        end_frame = child.parm("f2").eval()
        if child.parm("trange").eval() == 0:
            pass
        elif any(word in child.name().lower() for word in ["control", "preview", "single"]):
            pass
        elif "CACHE" in child.name().upper():
            render_nodes['cache_nodes'].append((child.name(), end_frame))
            cache_nodes.append(child.name())
        else:
            render_nodes['rop_nodes'].append((child.name(), end_frame))
            rop_nodes.append(child.name())
    cache_nodes = str(cache_nodes).strip("[]").translate(None, "'")
    rop_nodes = str(rop_nodes).strip("[]").translate(None, "'")
    # return cache_nodes, rop_nodes
    return render_nodes


def get_max_frame(out_node):
    # max_frame = int(max(child.parm("f2").eval() for child in out.children()))
    max_frames = []
    for child in out_node.children():
        try:
            max_frames.append(child.parm("f2").eval())
        except AttributeError:
            pass
    return int(max(max_frames))


def delete_section(file, section):
    config_handle = ConfigParser.RawConfigParser()
    config_handle.read(file)
    config_handle.remove_section(section)
    with open(file, "w") as f:
        config_handle.write(f)


def get_output_extension(out_node):
    cache_extension = None
    rop_extension = None
    for child in out_node.children():
        if "CONTROL" not in child.name().upper():
            #It's a ROP node
            try:
                output_file = child.parm("vm_picture").eval()
                rop_extension = output_file.split("\\")[-1].split(".")[-1]
            except AttributeError:
            #It's a CACHE node
                try:
                    output_file = child.parm("sopoutput").eval()
                    file_extension = output_file.split("\\")[-1].split(".")[-1]
                    if file_extension is 'sc':
                        cache_extension = 'bgeo.sc'
                    else:
                        cache_extension = file_extension
                except AttributeError:
                    pass
    return cache_extension, rop_extension



def write(config_file, out):
    config_handle = ConfigParser.RawConfigParser()
    HIPNAME = hou.expandString("$HIPNAME").split("\\")[-1]
    cache_nodes = get_rop_nodes_list(out)["cache_nodes"]
    config_handle.add_section("{}".format(HIPNAME))
    config_handle.set('{}'.format(HIPNAME), 'project_name', HIPNAME)
    config_handle.set('{}'.format(HIPNAME), 'rop_nodes',
                      get_rop_nodes_list(out)["rop_nodes"])
    config_handle.set('{}'.format(HIPNAME), 'rop_extension',
                      get_output_extension(out)[1])
    if cache_nodes:
        config_handle.set('{}'.format(HIPNAME), 'cache_nodes', cache_nodes)
        config_handle.set('{}'.format(HIPNAME), 'cache_extension',
                          get_output_extension(out)[0])
    with open(config_file, 'a') as configfile:
        config_handle.write(configfile)
    print(get_rop_nodes_list(out))


def check_projects(config_file, project_name):
    config_handle = ConfigParser.RawConfigParser()
    config_handle.read(config_file)
    return project_name in config_handle.sections()


def main():
    project = "powerup"
    HIPFILE = "E:\Videos\Houdini\\{}\\{}.hip".format(project, project)
    config_file = "E:\\Code\\NSR\\toRender.cfg"

    try:
        hou.hipFile.load(HIPFILE)
    except hou.LoadWarning as e:
        print(e)
    out = hou.node('/out')

    HIPNAME = hou.expandString("$HIPNAME").split("\\")[-1]

    if check_projects(config_file, HIPNAME):
        print("Configuration for {} already exists in toRender, replacing it...".format(
            HIPNAME))
        delete_section(config_file, HIPNAME)
        write(config_file, out)
    else:
        write(config_file, out)


if __name__ == "__main__":
    main()
