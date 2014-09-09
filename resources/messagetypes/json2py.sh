#!/bin/bash

# we cannot generate it as a structure of CONST because some numeric values are synonyms.
# One string value can map to many numeric values
# so we have to make a map: numeric value -> string value that is defined manually

for file in $@; do
  echo > /tmp/dic

  echo "  DICTIONARY = {" >> /tmp/dic
  export DICT_KEY
  bn=$(basename $file .json)
  echo "class ${bn}(object):" > ${bn}.py
  grep : $file | while read line; do
    CLEANED=$(echo $line | sed 's/"//g' )
    CONST_NAME=$(echo $CLEANED | cut -d: -f2 | tr ., _\ | tr -d ' ')
    VALUE=$(echo $CLEANED | cut -d: -f1)
    echo "  $CONST_NAME= $VALUE" >> ${bn}.py
    echo "    $VALUE: \"$CONST_NAME\"," >> /tmp/dic
  done
  echo >> ${bn}.py
  echo " } " >> /tmp/dic
  cat /tmp/dic >> ${bn}.py
  cat /tmp/dic
done
#cat >> ${bn}.py <<EOF 
#  @staticmethod
#  def DICTIONARY():
#    return {${bn}.__dict__[a]:str(a) for a in ${bn}.__dict__ if isinstance(${bn}.__dict__[a], (int,long))}
#EOF
#done
