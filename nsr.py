#!V:\Programs\Side Effects Software\Houdini 15.5.607\bin\hython.exe

import os
import hou
import glob
import ConfigParser as CP

'''
Takes need to be set inside Houdini

output format must be:
    PROJECT_NAME.ROP_NODE_NAME.FRAME.EXTENSION

READ CACHE FILES MUST HAVE FULL PATH



'''


conf = CP.ConfigParser()
conf.read('toRender.cfg')
HOUDINI_FOLDER = "E:\Videos\Houdini"


def get_last_frame(project_directory, END_FRAME, rop_node):
    _ = glob.glob("{}\\*.{}.*.*".format(project_directory, rop_node))
    if not _:
        return 1  # nothing was rendered yet
    frame_nums = sorted([int(file.split('.')[2]) for file in _])
    for frame in frame_nums:
        if int(frame) >= END_FRAME:
            return None
    return int(frame)


def render(HOUDINI_FOLDER, PROJECT_NAME, HIPFILE, frame, extension, rop_node="mantra1"):
    try:
        hou.hipFile.load(HIPFILE)
    except hou.OperationFailed as e:
        return "Not possible to load file {} - {}".format(HIPFILE, e)
    render_node = hou.node("/out/{}".format(rop_node))
    operator_name = render_node.name()
    render_node.parm('trange').set(1)

    if extension is None:
        extension = render_node.parm("vm_device").eval()

    path = "{}\\{}\\render\{}.{}.{}.{}".format(
        HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, operator_name, frame, extension)

    render_node.render(frame_range=(frame, frame),
                       output_file=path, verbose=True, output_progress=False)


def main():
    for project in conf.sections():
        PROJECT_NAME = conf.get(project, 'project_name')

        try:
            HIP_EXTENSION = conf.get(project, 'hip_extension')
        except CP.NoOptionError:
            HIP_EXTENSION = 'hip'

        try:
            OUT_EXTENSION = conf.get(project, 'out_extension')
        except CP.NoOptionError:
            OUT_EXTENSION = None  # Uses default defined in the ROP node, defined in func render

        try:
            ROP_NODES = [node.strip()
                         for node in conf.get(project, 'rop_nodes').split(',')]
        except CP.NoOptionError:
            # Uses default defined in the ROP node, defined in func render
            ROP_NODES = ['mantra1']

        RENDER_FOLDER = "{}\\{}\\render".format(HOUDINI_FOLDER, PROJECT_NAME)

        HIPFILE = "{}\\{}\\{}.{}".format(
            HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, HIP_EXTENSION)

        END_FRAME = int(conf.get(project, 'end_frame'))

        for rop_node in ROP_NODES:
            START_FRAME = get_last_frame(RENDER_FOLDER, END_FRAME, rop_node)
            if START_FRAME:
                for frame in range(START_FRAME, END_FRAME + 1):
                    render(HOUDINI_FOLDER, PROJECT_NAME,
                           HIPFILE, frame, OUT_EXTENSION, rop_node)

            else:
                print("Nothing to render in {} from {}!".format(rop_node, project))

if __name__ == "__main__":
    main()
