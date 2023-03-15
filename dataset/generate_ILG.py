import json
import pandas as pd
import numpy as np
import pyarrow as pa
import random
import os
import base64
from io import BytesIO

from tqdm import tqdm
import jsonpath
import csv
import pickle
import re

from PIL import Image, ImageDraw, ImageFile, ImageEnhance, ImageFont
#font = ImageFont.truetype('arialuni.ttf', 28)
ImageFile.LOAD_TRUNCATED_IMAGES = True

all_objects_meta = np.load('../../simmcdata/all_objects_meta.npy',allow_pickle=True).item()

row_act = ['REQUEST:GET', 'ASK:GET', 'REQUEST:ADD_TO_CART', 'INFORM:GET', 'INFORM:REFINE', 'INFORM:DISAMBIGUATE', 'REQUEST:COMPARE', 'INFORM:COMPARE', 'REQUEST:DISAMBIGUATE', 'CONFIRM:ADD_TO_CART']
converted_act = ['request get', 'ask get', 'request add to cart', 'inform get', 'inform refine', 'inform disambiguate', 'request compare', 'infrom compare', 'request disambiguate', 'compare add to cart']

with open('../../simmcdata/item2id.json', 'r') as f:
    item2id = json.load(f)

#with open('simmc2_background_item.json', 'r') as f:
#    all_background_item = json.load(f)

#id2item = {value:key for key,value in item2id.items()}

class ILG:
    def __init__(self, sceneImg_name, scene_assetIDs):
        self.sceneImg_name = sceneImg_name
        self.asset2bgitem = {}
        for assetID in scene_assetIDs:
            self.asset2bgitem[assetID] = {
                'global_id': '',
                'bgitems': []
            }

ILG_set = {}

def test():
    aILG = ILG('try', [1,2,3,4])
    aILG.asset2bgitem[1].append(['blue t-shirt', 'on', 'top row', 'of', 'display table', 3])
    aILG.asset2bgitem[2].append(['yellow jacket', 'on', 'floor rack', 2])
    print(aILG.asset2bgitem[2])


def get_json_value(json_data, key_name):
    key_value = jsonpath.jsonpath(json_data, '$..{key_name}'.format(key_name=key_name))
    return key_value
    
def get_dict_value(date, keys, default=None):
    # default=None，在key值不存在的情况下，返回None
    keys_list = keys.split('.')
    # 以“.”为间隔，将字符串分裂为多个字符串，其实字符串为字典的键，保存在列表keys_list里
    if isinstance(date, dict):
        # 如果传入的数据为字典
        dictionary = dict(date)
        # 初始化字典
        for i in keys_list:
            # 按照keys_list顺序循环键值
            try:
                if dictionary.get(i) != None:
                    dict_values = dictionary.get(i)
                # 如果键对应的值不为空，返回对应的值
                elif dictionary.get(i) == None:
                    dict_values = dictionary.get(int(i))
                # 如果键对应的值为空，将字符串型的键转换为整数型，返回对应的值
            except:
                return default
                # 如果字符串型的键转换整数型错误，返回None
            dictionary = dict_values
        return dictionary
    else:
        # 如果传入的数据为非字典
        try:
            dictionary = dict(eval(date))
            # 如果传入的字符串数据格式为字典格式，转字典类型，不然返回None
            if isinstance(dictionary, dict):
                for i in keys_list:
                    # 按照keys_list顺序循环键值
                    try:
                        if dictionary.get(i) != None:
                            dict_values = dictionary.get(i)
                        # 如果键对应的值不为空，返回对应的值
                        elif dictionary.get(i) == None:
                            dict_values = dictionary.get(int(i))
                        # 如果键对应的值为空，将字符串型的键转换为整数型，返回对应的值
                    except:
                        return default
                        # 如果字符串型的键转换整数型错误，返回None
                    dictionary = dict_values
                return dictionary
        except:
            return default

def getNonRepeatList(data):
    new_data = []
    for i in range(len(data)):
        if data[i] not in new_data:
            new_data.append(data[i])
    return new_data

def paste_region(src_img, tar_img, bbox):

    x1, y1, h, w = bbox[0], bbox[1], bbox[2], bbox[3]
    x2, y2 = x1+w, y1+h

    region = src_img.crop((x1,y1,x2,y2))
    tar_img.paste(region, (x1,y1,x2,y2))

    return tar_img, [str(x1), str(y1), str(x2), str(y2)]

def read_scene(single_scene):

    scene_name = single_scene

    with open(f"../../simmcdata/public/{single_scene}_scene.json", 'r', encoding='utf-8-sig', errors='ignore') as f:
        scene_info = json.load(f, strict=False)
    all_id = get_json_value(scene_info, 'index')
    
    all_prefab = get_json_value(scene_info, 'prefab_path')
    all_bbox = get_json_value(scene_info, 'bbox')

    scene_name = single_scene
    single_scene_new = single_scene[2:] + ".png"
    single_scene_1  = single_scene + ".png"
    part1 = '../../simmcdata/simmc2_scene_images_dstc10_public_part1'
    part2 = '../../simmcdata/simmc2_scene_images_dstc10_public_part2'
    if os.path.exists(part1+"/"+single_scene_1):
        single_scene = part1+"/"+single_scene_1
    elif os.path.exists(part2+"/"+single_scene_1):
        single_scene = part2+"/"+single_scene_1
    elif os.path.exists(part2+"/"+single_scene_new):
        single_scene = part2+"/"+single_scene_new
    elif os.path.exists(part1+"/"+single_scene_new):
        single_scene = part1+"/"+single_scene_new

    if os.path.basename(single_scene) == 'cloth_store_1416238_woman_4_8.png' or os.path.basename(single_scene) == 'cloth_store_1416238_woman_19_0.png':
        single_scene = None

    if scene_name not in ILG_set.keys():
        ILG_set[scene_name] = ILG(single_scene, all_id)

    return all_id, all_bbox, all_prefab, single_scene, scene_name

def get_act(turn, area):

    act = get_dict_value(turn, area, None)
    act_index = row_act.index(act)
    act = converted_act[act_index]

    return act

def get_request_slots(turn, area):

    request_slot_list = []
    request_slots = get_dict_value(turn, area, None)
    for slot in request_slots:
        if slot == 'availableSizes':
            slot = 'available sizes'
        elif slot == 'sleeveLength':
            slot = 'sleeve length'
        elif slot == 'customerReview':
            slot = 'customer review'
        elif slot == 'assetType':
            slot = 'assert type'
        request_slot_list.append(slot)

    return request_slot_list

def get_slot_values(turn, area):

    slot = get_dict_value(turn, area, None)

    slot_keys = []
    processed_slot = []
    if slot:
        objects_slot = list(slot.values())
        if not isinstance(objects_slot[0], dict):
            objects_slot = [slot]
        elif 'system' not in area:
            print(slot)
        
        for object_slot in objects_slot:
            for key, value in object_slot.items():
                if isinstance(value, list):
                    text = ''
                    for q in value:
                        text = text + str(q) + ' '
                    value = text

                if key == 'availableSizes':
                    key = 'available sizes'
                elif key == 'sleeveLength':
                    key = 'sleeve length'
                elif key == 'customerReview':
                    key = 'customer review'
                elif key == 'assetType':
                    key = 'assert type'

                slot_keys.append(key)
                n = str(key) + ':' + str(value)
                processed_slot.append(n)
        processed_slot = getNonRepeatList(processed_slot) 

    return processed_slot, slot_keys

def get_metadata(prefab_item, metadata_type):

    if metadata_type == 'non-visual':
        exclude_attr = ['color', 'pattern', 'type', 'sleeve length', 'asset type']
    elif metadata_type == 'visual': 
        exclude_attr = ['brand', 'price', 'size', 'materials', 'customer review', 'available sizes']
    else:
        exclude_attr = []

    obj_meta = ''         
    object_special_id = item2id[prefab_item]
    for attr_name, attr_value in all_objects_meta[object_special_id].items():

        attr_name = attr_name.replace('_', ' ')
        if attr_name in exclude_attr:
            continue

        if attr_name == 'available sizes':
            av_list = []
            for av_size in attr_value:
                if av_size == '<A>':
                    av_list.append('XS')
                elif av_size == '<B>':
                    av_list.append('S')
                elif av_size == '<C>':
                    av_list.append('M')
                elif av_size == '<D>':
                    av_list.append('L')
                elif av_size == '<E>':
                    av_list.append('XL')
                else:
                    av_list.append('XXL')
            attr_value = str(av_list).replace('\'','')

        if str(attr_value) != '':
            #obj_meta = obj_meta + str(attr_name) + ':' + str(attr_value) + ', '
            obj_meta = obj_meta + str(attr_value) + ', '

    obj_meta = obj_meta.replace('_', ' ')

    return obj_meta

def convert_bbox(bbox):

    x0, y0, h, w = bbox[0], bbox[1], bbox[2], bbox[3]
    x1, y1 = x0+w, y0+h

    converted_bbox = f"{x0},{y0},{x1},{y1}"

    return converted_bbox

def get_mentioned_obj(all_id, all_bbox, all_prefab, temp_obj_id):

    final_globalid, final_sceneid, final_bbox, final_visual, final_nonvisual = [], [], [], [], []
    for idx in temp_obj_id:
        for i, obj_id in enumerate(all_id):
            if int(idx) == int(obj_id):
                final_sceneid.append(idx)

                converted_bbox = convert_bbox(all_bbox[i])
                final_bbox.append(converted_bbox)

                prefab = all_prefab[i]
                global_id = item2id[prefab][2:-1]
                final_globalid.append(global_id)

                obj_visual = get_metadata(prefab, 'visual')
                final_visual.append(obj_visual)
                obj_nonvisual = get_metadata(prefab, 'non-visual')
                final_nonvisual.append(obj_nonvisual)

    return final_globalid, final_sceneid, final_bbox, final_visual, final_nonvisual



def generate_ILG(cur_response, scene_img, scene_ids, global_ids, all_bboxs, all_ids, file_path):
    colors = [all_objects_meta[f'<@{global_id}>']['color'] for global_id in global_ids]
    types = [all_objects_meta[f'<@{global_id}>']['type'] for global_id in global_ids]
    color_type = [f'{color} {type}' for color, type in zip(colors, types)]

    clean_colors = [' '.join(color.replace(',', '').strip().split()) for color in colors]

    response = cur_response.replace('?', ' ?').replace('.', ' .').replace(',', ' ,').replace('Take a look at ', '').replace('at this time', '').replace('at this moment', '').replace('to your criteria to show', '').strip()
    extracted_pos = re.findall('(towards|toward|to|along|against|at|in|on|below|behind) (top|front|the|this|our|your) (.*?) (,|\.|and\s|is\s|that\s|\?|as\s|has\s|are\s|which\s|in\s|or\s|have|costs|comes|does|also|would|might|match|may|I|fit|meet|exceed|will|suit|both|could|What|Currently|made|Garden)', response)
    extracted_obj = re.findall('(The|the|a|this|that|another|other|to) (\w*|\w* \w*|\w* \w* and \w*|\w* and \w*|\w* , \w* and \w*|\w* , \w*|\w*-\w*|\w* , \w* , and \w*) (couch|blazer|option|bed|tee|table|sofa|rug|trousers|hoodie|jeans|coat|jackets|jacket|dress|shirt|pants|blouse|one|ones|sweater|pair) (comes|has|right|costs|just|is|which|the|you|toward|to|along|against|at|in|on|or|up|and|hanging|facing|\?|\.)', response)

    obj = [obj_item[1:-1] for obj_item in extracted_obj]
    pos = [' '.join(pos_item[:-1]) for pos_item in extracted_pos]

    obj_item_str_, obj_scene_id_, obj_global_id_, item_ = [], [], [], []
    if (len(scene_ids) == 1 and len(extracted_pos) == 1) or (len(scene_ids) == 2 and len(extracted_pos) == 2):
        obj_item_str_, obj_scene_id_, obj_global_id_, item_ = color_type, scene_ids, global_ids, pos

    elif (len(scene_ids) == 3 and len(extracted_pos) == 3):
        if len(scene_ids) == len(extracted_obj):
            obj_color = [' '.join(' '.join(obj_item[:-1]).replace(',', '').replace('and ', '').strip().split()) for obj_item in obj]
            if list(obj_color) == list(clean_colors):
                obj_item_str_, obj_scene_id_, obj_global_id_, item_ = color_type, scene_ids, global_ids, pos

    elif len(scene_ids) == 3 and len(extracted_pos) == 1 and len(cur_response) < 70:
        obj_item_str_, obj_scene_id_, obj_global_id_, item_ = color_type, scene_ids, global_ids, pos*3


    multiobj_str, multiobj_pos, multiobj_idspos = [], [], []
    for i, pos_answer in enumerate(item_):
        if ('cart' in pos_answer) or ('size' in pos_answer) or ('price' in pos_answer) or ('in this pattern' in pos_answer) or ('inventory' in pos_answer):
            continue
        else:
            obj_item_str, obj_scene_id, obj_global_id = obj_item_str_[i], obj_scene_id_[i], obj_global_id_[i]
            if obj_scene_id in all_ids:
                #print(' ')
                #print(pos_answer)
                prep = re.findall('in\s|on\s|of\s|above\s|below\s|at\s|to\s|behind\s|along\s|against\s|towards\s|toward\s',  pos_answer)
                prep_len = len(prep[0])
                ILG_set[scene_img].asset2bgitem[obj_scene_id]['global_id'] = obj_global_id
                ILG_set[scene_img].asset2bgitem[obj_scene_id]['bgitems'].append([obj_item_str, prep[0].strip(), pos_answer[prep_len:], len(prep)])
                print(prep)
                print(ILG_set[scene_img].asset2bgitem[obj_scene_id])


def read_turn(history_turns, curr_scene, curr_turn_id, all_id_list, all_bbox_list, all_prefab_list, scene_list, agent, file_path, split, end_flag):

    history_ = []
    for turn in history_turns:
        history_.append(get_dict_value(turn, 'transcript', None))
        history_.append(get_dict_value(turn, 'system_transcript', None))

    if agent == 'system_':
        cur_response = history_[-1]
        history = ' '.join(history_[:-1])
    else:
        cur_response = history_[-2]
        history = ' '.join(history_[:-2])     

    curr_turn = history_turns[-1]
    act = get_act(curr_turn, f'{agent}transcript_annotated.act')
    temp_obj_id = get_dict_value(history_turns[-1], f'{agent}transcript_annotated.act_attributes.objects', None)

    sceneid_list, globalid_list, turn_sceneid_list, turn_globalid_list, turn_bbox_list = [], [], [], [], []
    for i in range(len(scene_list)):
        if scene_list[i] == None: continue

        all_id, all_bbox, all_prefab, scene_name = all_id_list[i], all_bbox_list[i], all_prefab_list[i], curr_scene[i]
        turn_globalid, turn_sceneid, turn_bbox, turn_visual, turn_nonvisual = get_mentioned_obj(all_id, all_bbox, all_prefab, temp_obj_id)

        turn_sceneid_list.append(turn_sceneid)
        turn_globalid_list.append(turn_globalid)
        turn_bbox_list.append(turn_bbox)

        for global_id, sceneid, bbox, obj_visual, obj_nonvisual in zip(turn_globalid, turn_sceneid, turn_bbox, turn_visual, turn_nonvisual):
            if sceneid not in sceneid_list:
                sceneid_list.append(sceneid)
                globalid_list.append(global_id)

    if set(temp_obj_id) == set(sceneid_list) and len(temp_obj_id) > 0 and ('cart' not in act) and ('disambiguate' not in act):
        for i in range(len(scene_list)):
            if scene_list[i] == None: continue
            if (split == 'devtest' and end_flag == True): continue
            generate_ILG(cur_response, curr_scene[i], sceneid_list, globalid_list, all_bbox_list[i], all_id_list[i], file_path)


def main(split, file_path):

    with open(f'../../simmcdata/simmc2_dials_dstc10_{split}.json', 'r') as datafile:
        data = json.load(datafile)
    
    all_dialogues = get_json_value(data, 'dialogue')
    all_scene_id = get_json_value(data, 'scene_ids')
    all_mentioned_id = get_json_value(data, 'mentioned_object_ids')

    for i in tqdm(range(len(all_dialogues))):
        curr_dialogue, curr_scene, curr_mentioned_id = all_dialogues[i], all_scene_id[i], all_mentioned_id[i]

        scene_name, scene_list, all_id_list, all_bbox_list, all_prefab_list = [], [], [], [], []
        for scene_num, single_scene in enumerate(curr_scene.values()):
            all_id, all_bbox, all_prefab, single_scene, img_path = read_scene(single_scene)
            
            if single_scene != None: 
                for item, list in zip([all_id, all_bbox, all_prefab, single_scene, img_path], [all_id_list, all_bbox_list, all_prefab_list, scene_list, scene_name]):
                    list.append(item)
            else:
                continue
        
        if len(scene_list) == 1: scene_list.append(None)
        if len(scene_list) == 0: continue

        end_flag = False
        for j, _ in enumerate(curr_dialogue):

            if j == len(curr_dialogue)-1: 
                end_flag = True

            history_turns = []
            for k in np.arange(j+1):
                history_turns.append(curr_dialogue[k])
            curr_turn_id = i * 100 + j

            #for agent in ['', 'system_']:
            for agent in ['system_']:
                read_turn(history_turns, scene_name, curr_turn_id, all_id_list, all_bbox_list, all_prefab_list, scene_list, agent, file_path, split, end_flag)

            
if __name__ == '__main__':

    #os.mkdir('simmc2_QA')
    file_path = f'simmc2_QA/simmc2_PosVisQA_all_revised.tsv'

    if os.path.exists(file_path): os.remove(file_path)
    if os.path.exists(f'{file_path}.index'): os.remove(f'{file_path}.index')

    main('train', file_path)
    main('dev', file_path)
    main('devtest', file_path)
    
    pickle.dump(ILG_set, open('ILGs.pkl', 'wb'))

