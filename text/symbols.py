""" from https://github.com/keithito/tacotron """


_pad = "_"
_punctuation = "!'(),.:;? "
_special = "-"
_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_letters_vn = "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹýÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ"
_mfa_phoneset = ["@" +  i for i in "aː˦˥ aː˨˨ aː˨˩ aː˨˩˦ aː˨˩˨ a˦˥ a˨˨ a˨˩ a˨˩˦ a˨˩˨ c eː˦˥ eː˨˨ eː˨˩ eː˨˩˦ eː˨˩˨ f h iə˦˥ iə˨˨ iə˨˩ iə˨˩˦ iə˨˩˨ iː˦˥ iː˨˨ iː˨˩ iː˨˩˦ iː˨˩˨ i˦˥ i˨˨ i˨˩ i˨˩˦ i˨˩˨ j k kp l m n oː˦˥ oː˨˨ oː˨˩ oː˨˩˦ oː˨˩˨ o˦˥ o˨˨ o˨˩ o˨˩˦ o˨˩˨ p r s t tʰ uə˦˥ uə˨˨ uə˨˩ uə˨˩˦ uə˨˩˨ uː˦˥ uː˨˨ uː˨˩ uː˨˩˦ uː˨˩˨ u˦˥ u˨˨ u˨˩ u˨˩˦ u˨˩˨ v w x ŋ ŋm ɓ ɔː˦˥ ɔː˨˨ ɔː˨˩ ɔː˨˩˦ ɔː˨˩˨ ɔ˦˥ ɔ˨˨ ɔ˨˩ ɔ˨˩˦ ɔ˨˩˨ ɗ əː˦˥ əː˨˨ əː˨˩ əː˨˩˦ əː˨˩˨ ə˦˥ ə˨˨ ə˨˩ ə˨˩˦ ə˨˩˨ ɛː˦˥ ɛː˨˨ ɛː˨˩ ɛː˨˩˦ ɛː˨˩˨ ɡ ɨə˦˥ ɨə˨˨ ɨə˨˩ ɨə˨˩˦ ɨə˨˩˨ ɨː˦˥ ɨː˨˨ ɨː˨˩ ɨː˨˩˦ ɨː˨˩˨ ɨ˦˥ ɨ˨˨ ɨ˨˩ ɨ˨˩˦ ɨ˨˩˨ ɲ ʈ ʔ".split()]
_silences = ["@sp", "@spn", "@sil"]

# Export all symbols:
symbols = (
    [_pad]
    + list(_special)
    + list(_punctuation)
    + list(_letters)
    + list(_letters_vn)
    + _mfa_phoneset
    + _silences
)
