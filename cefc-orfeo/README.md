# CEFC — Corpus d'Études du Français Contemporain

Le Corpus d'Études du Français Contemporain est composé de corpus oraux et écrits. 
oral : cfpp, clapi, coralrom, crfp, fleuron, frenchoralnarrative, husianycia, ofrom, tcof, tufs, valibel
écrit : annodis, chambers-rostand, comere, est-republicain, frantext, scientext

Ces corpus sont décrits sur la page http://www.projet-orfeo.fr/corpus-source/

## Guidelines 

Les guides d'annotation sont disponibles sur le site du projet Orfeo à l'adresse : http://www.projet-orfeo.fr/guides/
*  Guide de segmentation
*  Guide d'annotation morpho-syntaxique (POS)
*  Guide d'annotation syntaxique

Pour chaque fichier du corpus CEFC on trouve un fichier .xml contenant les métadonnées et un fichier .orfeo contenant
les données et les annotations. Les fichiers des corpus oraux sont accompagnés d'un fichier son au format wav.

## Format des fichiers .orfeo

Les fichiers .orfeo sont des fichiers tsv (tab separated value). Le format est similaire au [format CoNLL-U](http://universaldependencies.org/format.html) avec 3 colonnes supplémentaires pour les estampilles temporelles et l'identification du locuteur


1. ID
2. FORM
3. LEMMA
4. POS
5. POS
6. FEATS (always void)
7. HEAD
8. DEPREL
9. DEPS (always void)
10. MISC (always void)
11. BTIMESTAMP: begin timestamp in ms
12. ETIMESTAMP: end timestamp in ms
13. SPEAKERID: the id of the speaker (``xml:id`` attribute value of the ``person`` element in metadata file)

## Liste des catégories morphosyntaxiques (POS)

``ADJ`` (adjectifs qualificatifs) : méchant, petit, long, gigantesque, drôle, rouge, etc.  
``ADN`` (adverbes de négation) : pas, jamais, nullement, guère, plus, etc.  
``ADV`` (adverbes) : savamment, peut-être, in extremis, très, environ, etc.  
``CLI`` (autres clitiques) : te, lui, -le, -y, en, -leur, nous, etc.  
``CLN`` (clitique de négation) : ne  
``CLS`` (clitiques sujets) : tu, elles, vous, -vous, c’,  etc.  
``COO`` (conjonctions de coordination) : et, ou, alias, mais encore, voire, puis, etc.  
``CSU`` (conjonctions de subordination) : au fur et à mesure qu’,  alors que, lorsque, etc.  
``DET`` (déterminants) : cette, certains, quelques, un, etc.  
``INT`` (interjections) : hein, ben, allô, pfff, no comment, niark, okidoki, parbleu, etc.  
``NOM`` (noms) : diplodocus, Montastruc-la-Conseillère, topinambour, Google, etc.  
``NUM`` (nombres) : six, treize, milliard, quatorze, mille, billion, dix-sept, quatre-vingt-onze, vingt-cinq, etc. (mais pas soixante et n)  
``PCT`` (signes de ponctuation) : !, ?, !, etc., (, », etc.  
``PRE`` (prépositions) : de, des, nonobstant, parmi, pour cause de, par delà, outre, etc.  
``PRO`` (pronoms) : moi, celles, les tiens, plusieurs, vous-mêmes, nul, pas grand-chose, etc.  
``PRQ`` (pronoms interrogatifs-relatifs) : combien est-ce que, lequel, pourquoi, que, etc.  
``VNF`` (verbes à l'infinitif) : tenir, poindre, jouer, entendre, etc.  
``VPP`` (verbes au participe passé) : tenu, point, joué, entendu, etc.  
``VPR`` (verbes au participe présent) : tenant, poignant, jouant, entendant, etc.  
``VRB`` (verbes à la forme finie) : tiens, poignent, joueraient, entendissions, etc.  
``X`` (mot inconnu, étranger ou tronqué de catégorie indécidable) : El Paìs, fuck you, etc.  

## Liste des relations syntaxiques
### microsyntaxe
``root`` (racine)  
``dep`` (dépendant, complément ou ajout)  
``subj`` (sujet)  
``aux`` (auxiliaire)  
``spe`` (spécifieur)  
``disflink`` (segment non analysable)  

### liens paradigmatiques 
``para`` (lien paradigmatique)  
``mark`` (lien marqueur)  

### macrosyntaxe
``periph`` (éléments périphériques)  
``dm`` (marqueurs de discours)  