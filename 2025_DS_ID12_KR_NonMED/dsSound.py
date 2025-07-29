'''' Guide sound '''
import winsound
from dsSetting import dsParam

guideSound = {
    'intro_main': '',
    'intro_menu': '',
    'intro_menu_for_train': './ui/sound/intro_menu_for_train.wav',
    'intro_threshold': './ui/sound/intro_threshold.wav',
    'intro_discrimination': './ui/sound/intro_discrimination.wav',
    'intro_identification': './ui/sound/intro_identification.wav',
    'intro_train_st': './ui/sound/intro_train_st.wav',
    'intro_train_id': './ui/sound/intro_train_id.wav',
    'ready_test': '',
    'try_scent_threshold': './ui/sound/try_scent_threshold.wav',
    'progress_scent': './ui/sound/progress_scent.wav',
    'progress_scent_1': './ui/sound/progress_scent_1.wav',
    'progress_scent_2': './ui/sound/progress_scent_2.wav',
    'progress_scent_3': './ui/sound/progress_scent_3.wav',
    'progress_scent_train': './ui/sound/progress_scent_train.wav',
    'scent_emit': './ui/sound/scent_emit.wav',
    'scent_emit_threshold_practice': './ui/sound/scent_emit_threshold_practice.wav',
    'scent_emit_threshold': './ui/sound/scent_emit_threshold.wav',
    'scent_emit_discrimination': './ui/sound/scent_emit_discrimination.wav',
    'scent_emit_identification': './ui/sound/scent_emit_identification.wav',
    'question_threshold': './ui/sound/question_threshold.wav',
    'question_discrimination': './ui/sound/question_discrimination.wav',
    'question_identification': './ui/sound/question_identification.wav',
    'select_train_st': './ui/sound/select_train_st.wav',
    'select_train_id': './ui/sound/select_train_id.wav',
    'rate_train_st': './ui/sound/rate_train_st.wav',
    'result_threshold': './ui/sound/result_threshold.wav',
    'result_discrimination': './ui/sound/result_discrimination.wav',
    'result_identification': './ui/sound/result_identification.wav',
    'records_train_st': './ui/sound/records_train_st.wav',
    'end_threshold': './ui/sound/end_threshold.wav',
    'end_discrimination': './ui/sound/end_discrimination.wav',
    'end_identification': './ui/sound/end_identification.wav',
    'test_results': './ui/sound/test_results.wav',
    'cleaning_caution': './ui/sound/cleaning_caution.wav',
}

trainIDSound = {
    'train_id_main': './ui/sound/train_id/train_id_main.wav',
    'train_id_menu': './ui/sound/train_id/train_id_menu.wav',
    'train_id_thanks': './ui/sound/train_id/train_id_thanks.wav',

    'train_id_01_01': './ui/sound/train_id/train_id_01_01.wav',
    'train_id_01_02': './ui/sound/train_id/train_id_01_02.wav',
    'train_id_01_03': './ui/sound/train_id/train_id_01_03.wav',
    'train_id_01_04': './ui/sound/train_id/train_id_01_04.wav',
    'train_id_01_05': './ui/sound/train_id/train_id_01_05.wav',
        
    'train_id_02_01': './ui/sound/train_id/train_id_02_01.wav',
    'train_id_02_02': './ui/sound/train_id/train_id_02_02.wav',
    'train_id_02_03': './ui/sound/train_id/train_id_02_03.wav',
    'train_id_02_04': './ui/sound/train_id/train_id_02_04.wav',
    'train_id_02_05': './ui/sound/train_id/train_id_02_05.wav',
    
    'train_id_03_01': './ui/sound/train_id/train_id_03_01.wav',
    'train_id_03_02': './ui/sound/train_id/train_id_03_02.wav',
    'train_id_03_03': './ui/sound/train_id/train_id_03_03.wav',
    'train_id_03_04': './ui/sound/train_id/train_id_03_04.wav',
    'train_id_03_05': './ui/sound/train_id/train_id_03_05.wav',

    'train_id_04_01': './ui/sound/train_id/train_id_04_01.wav',
    'train_id_04_02': './ui/sound/train_id/train_id_04_02.wav',
    'train_id_04_03': './ui/sound/train_id/train_id_04_03.wav',
    'train_id_04_04': './ui/sound/train_id/train_id_04_04.wav',
    'train_id_04_05': './ui/sound/train_id/train_id_04_05.wav',
   
    'train_id_05_01': './ui/sound/train_id/train_id_05_01.wav',
    'train_id_05_02': './ui/sound/train_id/train_id_05_02.wav',
    'train_id_05_03': './ui/sound/train_id/train_id_05_03.wav',
    'train_id_05_04': './ui/sound/train_id/train_id_05_04.wav',
    'train_id_05_05': './ui/sound/train_id/train_id_05_05.wav',
    
    'train_id_06_01': './ui/sound/train_id/train_id_06_01.wav',
    'train_id_06_02': './ui/sound/train_id/train_id_06_02.wav',
    'train_id_06_03': './ui/sound/train_id/train_id_06_03.wav',
    'train_id_06_04': './ui/sound/train_id/train_id_06_04.wav',
    'train_id_06_05': './ui/sound/train_id/train_id_06_05.wav',
    
    'train_id_07_01': './ui/sound/train_id/train_id_07_01.wav',
    'train_id_07_02': './ui/sound/train_id/train_id_07_02.wav',
    'train_id_07_03': './ui/sound/train_id/train_id_07_03.wav',
    'train_id_07_04': './ui/sound/train_id/train_id_07_04.wav',
    'train_id_07_05': './ui/sound/train_id/train_id_07_05.wav',
    
    'train_id_08_01': './ui/sound/train_id/train_id_08_01.wav',
    'train_id_08_02': './ui/sound/train_id/train_id_08_02.wav',
    'train_id_08_03': './ui/sound/train_id/train_id_08_03.wav',
    'train_id_08_04': './ui/sound/train_id/train_id_08_04.wav',
    'train_id_08_05': './ui/sound/train_id/train_id_08_05.wav'
}

def playGuideSound(sound_name):
    winsound.PlaySound(None, winsound.SND_PURGE)
    if dsParam['voice_onoff'] == 1 and guideSound[sound_name] != '':
        winsound.PlaySound(guideSound[sound_name], winsound.SND_ASYNC)
        return True
    else:
        return False
    
def playTrainIDSound(sound_name):
    winsound.PlaySound(None, winsound.SND_PURGE)
    if dsParam['voice_onoff'] == 1 and trainIDSound[sound_name] != '':
        winsound.PlaySound(trainIDSound[sound_name], winsound.SND_ASYNC)
        return True
    else:
        return False