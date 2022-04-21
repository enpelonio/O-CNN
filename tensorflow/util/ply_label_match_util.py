label_file = '/home/ervin/Desktop/Thesis/O-CNN/tensorflow/script/sample_labels.txt'
ply_file = '/home/ervin/Desktop/Thesis/O-CNN/tensorflow/script/dataset/shapenet_segmentation/ply_reduced_10000_strict_byday/M0313/M01_0313_a.ply'

def get_labels_from_ply():
    ply = open(ply_file,'r')
    lines = ply.readlines()
    labels = []
    for line in lines:
        words = [x for x in line.replace('\n','').split(' ')]
        if len(words) > 6:
            labels.append(int(float(words[-1])))
    return labels

def get_labels_from_file():
    file = open(label_file,'r')
    lines = file.readlines()
    labels = []
    for line in lines:
        labels.append(int(float(line)))
    return labels

def is_equal():
    res = True
    labels_1 = get_labels_from_ply()
    labels_2 = get_labels_from_file()
    if len(labels_1) != len(labels_2):
        return False
    for i in range(len(labels_1)):
        if labels_1[i] != labels_2[i]:
            res = False
            break
    return res

print(is_equal())