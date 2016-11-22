import hou
import ConfigParser



def get_rop_nodes_list(out_node):
    rop_nodes = []
    cache_nodes = []
    for child in out_node.children():
        if "CACHE" in child.name().upper():
            cache_nodes.append(child.name())
        elif any(word in child.name().lower() for word in ["control", "preview"]):
            pass
        else:
            rop_nodes.append(child.name())
    cache_nodes = str(cache_nodes).strip("[]").translate(None, "'")
    rop_nodes = str(rop_nodes).strip("[]").translate(None, "'")
    return cache_nodes, rop_nodes


def get_max_frame(out_node):
    # max_frame = int(max(child.parm("f2").eval() for child in out.children()))
    max_frames = []
    for child in out_node.children():
        try:
            max_frames.append(child.parm("f2").eval())
        except AttributeError:
            pass
    return int(max(max_frames))


def get_output_extension(out_node):
    for child in out_node.children():
        if "CONTROL" not in child.name().upper():
            try:
                output_file = child.parm("vm_picture").eval()
                rop_extension = output_file.split("\\")[-1].split(".")[-1]
            except AttributeError:
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


def write(config_file, out, config_handle):
    HIPNAME = hou.expandString("$HIPNAME").split("\\")[-1]
    rop_nodes = get_rop_nodes_list(out)[1]
    cache_nodes = get_rop_nodes_list(out)[0]
    config_handle.add_section("{}".format(HIPNAME))
    config_handle.set('{}'.format(HIPNAME), 'project_name', HIPNAME)
    config_handle.set('{}'.format(HIPNAME), 'end_frame', get_max_frame(out))
    config_handle.set('{}'.format(HIPNAME), 'rop_nodes', get_rop_nodes_list(out)[1])
    config_handle.set('{}'.format(HIPNAME), 'rop_extension',
               get_output_extension(out)[1])
    if cache_nodes:
        config_handle.set('{}'.format(HIPNAME), 'cache_nodes', cache_nodes)
        config_handle.set('{}'.format(HIPNAME), 'cache_extension',
                   get_output_extension(out)[0])
    config_handle.write(config_file)
    config_file.close()


def main():
    f = "E:\Videos\Houdini\\abstract_will\\abstract_will.hip"
    w = "E:\Code\NSR\\toRender.cfg"
    conf = open(w, 'a+')
    Config = ConfigParser.ConfigParser()

    try:
        hou.hipFile.load(f)
    except hou.LoadWarning, e:
        print e

    out = hou.node('/out')

    write(conf, out, Config)

if __name__ == "__main__":
    main()
