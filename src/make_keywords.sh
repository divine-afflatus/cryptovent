#!/bin/bash

shopt -s expand_aliases

# | Field Id | Name                             | Explanation                                      |
# | -------- | -------------------------------- | ------------------------------------------------ |
# | 1        | token                            |                                                  |
# | 2-3      | tb_tf, tb_tp                     | C(w;tb), P(w;tb)                                 |
# | 4-5      | tb_df, tb_dp                     | C(d;tb), P(d;tb)                                 |
# | 6        | tb_tfidf                         | C(w;tb) / (1 + log(1 + C(d;tb)))                 |
# | 7-11     | tw_tf tw_tp tw_df tw_dp tw_tfidf | Same, but for Twitter data                       |
# | 12       | tbtw_kl                          | P(w;tb) * log (P(w;tb) / P(w;tw))                |
# | 13       | twtb_kl                          | P(w;tw) * log (P(w;tb) / P(w;tw))                |
# | 14       | tbtw_odds                        | log (P(w;tb) / P(w;tw))                          |

alias tawk="awk -F $'\t'"
alias tsort="sort -t $'\t'"
alias tjoin="join -t $'\t'"

STR=$(tawk '{ tf += $2; df += $3; } END { print tf " " df; }' $1)
TB_TF_TOTAL=$(cut -f1 -d$' ' <<< $STR)
TB_DF_TOTAL=$(cut -f2 -d$' ' <<< $STR)
STR=$(tawk '{ tf += $2; df += $3; } END { print tf " " df; }' $2)
TW_TF_TOTAL=$(cut -f1 -d$' ' <<< $STR)
TW_DF_TOTAL=$(cut -f2 -d$' ' <<< $STR)

# SORTED1="$(mktemp)"
# SORTED2="$(mktemp)"
# tsort $1 > $SORTED1
# tsort $2 > $SORTED2

LANG=C tjoin -j1 -o1.1,1.2,1.3,2.2,2.3 $1 $2 | tawk "{
	OFS=\"\\t\"
	tb_tf=\$2;
	tb_df=\$3;
	tw_tf=\$4;
	tw_df=\$5;
	tb_tp=tb_tf/$TB_TF_TOTAL; tb_dp=tb_df/$TB_DF_TOTAL;
	tw_tp=tw_tf/$TW_TF_TOTAL; tw_dp=tw_df/$TB_DF_TOTAL;
	tb_tfidf=tb_tf/(1 + log(1 + tb_df)); tw_tfidf=tw_tf/(1 + log(1 + tw_df));
	tbtw_kl=tb_tp * log(tb_tp/tw_tp); twtb_kl=tw_tp*log(tb_tp/tw_tp);
	tbtw_odds=log(tb_tp/tw_tp)
	print \$1, tb_tf, tb_tp, tb_df, tb_dp, tb_tfidf, 
	           tw_tf, tw_tp, tw_df, tw_dp, tw_tfidf,
	           tbtw_kl, twtb_kl, tbtw_odds; }"