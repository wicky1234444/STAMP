import pandas as pd
import numpy as np
from data_prepare.entity.sample import Sample
from data_prepare.entity.samplepack import Samplepack


def load_data_p(train_file, test_file, pro, pad_idx = 0):
    '''
    ret = [contexts, aspects, labels, positions] ,
    context.shape = [len(samples), None], None should be the len(context); 
    aspects.shape = [len(samples), None], None should be the len(aspect);
    labels.shape = [len(samples)]
    positions.shape = [len(samples), 2], the 2 means from and to.
    '''
    # the global param.
    items2idx = {}  # the ret
    items2idx['<pad>'] = pad_idx
    idx_cnt = 0
    # load the data
    train_data, idx_cnt = _load_data(train_file, items2idx, idx_cnt, pro,pad_idx)
    print(len(items2idx.keys()))
    test_data, idx_cnt = _load_data(test_file, items2idx, idx_cnt, pad_idx = pad_idx)
    print(len(items2idx.keys()))

    item_num = len(items2idx.keys())
    return train_data, test_data, items2idx, item_num



def _load_data(file_path, item2idx, idx_cnt, pro = None, pad_idx=0):

    data = pd.read_csv(file_path, sep='\t', dtype={'ItemId': np.int64})
    print("read finish")
    if pro is not None:
        session_ids = data.SessionId.value_counts().rename_axis("SessionId").reset_index(name="counts")
        session_ids = session_ids[0:100000]     #take only 1 lakh sessions
        data = data[data["SessionId"].isin(session_ids["SessionId"])]
        print("list finish")
        
    data.sort_values(['SessionId', 'Time'], inplace = True)
    print("sort finish")
    session_data = list(data['SessionId'].values)
    item_event = list(data['ItemId'].values)
    print("session_data length: ", len(session_data), "itemid length: ", len(item_event))
    '''if pro is not None:     ## skips first session
        #lenth = int(len(session_data) / pro)
        lenth = 100000  ##1lakh sessions
        print("pro none: ",lenth)
        session_data = session_data[-lenth:]
        item_event = item_event[-lenth:]
        for i in range(len(session_data)):
            if session_data[i] != session_data[i+1]:
                break
        session_data = session_data[i + 1:]
        item_event = item_event[i + 1:]'''
    lenth = len(session_data)
    print("after pro not none loop: ", lenth)

    samplepack = Samplepack()
    samples = []
    now_id = 0
    print("I am reading")
    sample = Sample()
    last_id = None
    click_items = []

    for s_id,item_id in zip(session_data, item_event):
        if last_id is None:
            last_id = s_id
        if s_id != last_id:
            item_dixes = []
            for item in click_items:
                if item not in item2idx:
                    if idx_cnt == pad_idx:
                        idx_cnt += 1
                    item2idx[item] = idx_cnt
                    idx_cnt += 1
                item_dixes.append(item2idx[item])
            in_dixes = item_dixes[:-1]
            out_dixes = item_dixes[1:]
            sample.id = now_id
            sample.session_id = last_id
            sample.click_items = click_items
            sample.items_idxes = item_dixes
            sample.in_idxes = in_dixes
            sample.out_idxes = out_dixes
            samples.append(sample)
            # print(sample)
            sample = Sample()
            last_id =s_id
            click_items = []
            now_id += 1
        else:
            last_id = s_id
        click_items.append(item_id)
        # click_items = list(tmp_data[session_tmp_idx]['ItemId'])
    sample = Sample()
    item_dixes = []
    for item in click_items:
        if item not in item2idx:
            if idx_cnt == pad_idx:
                idx_cnt += 1
            item2idx[item] = idx_cnt
            idx_cnt += 1
        item_dixes.append(item2idx[item])
    in_dixes = item_dixes[:-1]
    out_dixes = item_dixes[1:]
    sample.id = now_id
    sample.session_id = last_id
    sample.click_items = click_items
    sample.items_idxes = item_dixes
    sample.in_idxes = in_dixes
    sample.out_idxes = out_dixes
    samples.append(sample)
    print("last sample: ",sample)


    samplepack.samples = samples
    samplepack.init_id2sample()
    return samplepack, idx_cnt


