import os
import hou
import ConfigParser as CP

conf = CP.ConfigParser()
conf.read('toRender.cfg')
HOUDINI_FOLDER = "E:\Videos\Houdini"

def get_last_frame(project_directory, END_FRAME):
    files = os.listdir(project_directory)
    frame_nums = sorted([int(file.split('.')[2]) for file in files])
    for frame in frame_nums:
        if int(frame) >= END_FRAME:
            return None
    return int(frame)


# def output_path(HOUDINI_FOLDER, PROJECT_NAME, frame, operator_name, extension):
#     path = "{}\\{}\\render\{}.{}.{}.{}".format(
#         HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, operator_name, frame, extension)
    # return path


def render(HOUDINI_FOLDER, PROJECT_NAME, HIPFILE, frame, extension, rop_node="mantra1"):
    hou.hipFile.load(HIPFILE)
    render_node = hou.node("/out/{}".format(rop_node))
    operator_name = render_node.name()
    render_node.parm('trange').set(1)

    path = "{}\\{}\\render\{}.{}.{}.{}".format(
        HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, operator_name, frame, extension)

    render_node.render(frame_range=(frame, frame),
                       output_file=path, verbose=True, output_progress=True)


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
            OUT_EXTENSION = 'exr'

        RENDER_FOLDER = "{}\\{}\\render".format(HOUDINI_FOLDER, PROJECT_NAME)

        HIPFILE = "{}\\{}\\{}.{}".format(
            HOUDINI_FOLDER, PROJECT_NAME, PROJECT_NAME, HIP_EXTENSION)

        END_FRAME = int(conf.get(project, 'end_frame'))

        START_FRAME = get_last_frame(RENDER_FOLDER, END_FRAME)

        if START_FRAME:
            for frame in range(START_FRAME, END_FRAME + 1):
                render(HOUDINI_FOLDER, PROJECT_NAME, HIPFILE, frame, OUT_EXTENSION)
        else:
            print("Nothing to render in {}!".format(project))

if __name__ == "__main__":
    main()
