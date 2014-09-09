# By Chloe Desoutter <chloe.desoutter@atasta.net>
# Licensed under MIT license
class Identifier(object):
  @classmethod
  def find_candidates(s,int_value):
    import Common, Keynote, Numbers, Pages
    for item in [ Common.Common, Keynote.Keynote, Numbers.Numbers, Pages.Pages ]:
      dic = item.DICTIONARY
      if int_value in dic.keys():
        yield dic[int_value]
      else:
        pass

  @classmethod
  def to_classname(s,string):
    spl = string.split('_')
    return "".join(spl[1:])
if (__name__ == '__main__'):
  for i in Identifier.find_candidates(10000):
    print i
