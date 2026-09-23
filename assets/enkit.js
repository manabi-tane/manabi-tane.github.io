/* 英語の教材データを書くための道具。
   S(英文, [区切りごとの訳], 全文訳, {n:構文メモ, sv:骨組み})
     英文の「/」が意味のまとまりの区切り。訳の数は区切りの数と合わせる。
   V(語, 発音記号, 品詞, 意味, {n:メモ})  新出語 */
const S = (en, parts, ja, x) => Object.assign({en, parts, ja}, x || {});
const V = (w, ipa, pos, m, x) => Object.assign({w, ipa, pos, m}, x || {});
