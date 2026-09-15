# ba_meta require api 9
import random
import re
import builtins
import babase
import bascenev1 as bs
import bauiv1 as bui
from bauiv1lib.party import PartyWindow
# ba_meta export babase.Plugin

class CodeExecutor(babase.Plugin):
 def __init__(self):
  self._hooked=False
  self._original=None
  self._hook=None
  old=getattr(builtins,"_CODE_EXECUTOR_INSTANCE",None)
  if old is not None and old is not self:
   try:old.on_app_shutdown()
   except Exception:pass
  builtins._CODE_EXECUTOR_INSTANCE=self
  print("CodeExecutor: LOADED")
  babase.apptimer(0.0,babase.WeakCall(self._install))

 def _install(self):
  if self._hooked:return
  try:
   self._original=PartyWindow._send_chat_message
   owner=self
   def send_hook(window,*args,**kwargs):
    try:text=bui.textwidget(query=window._text_field)
    except Exception:text=""
    if owner._handle_command(window,text):return
    return owner._original(window,*args,**kwargs)
   self._hook=send_hook
   PartyWindow._send_chat_message=send_hook
   self._hooked=True
   print("CodeExecutor: HOOKED")
  except Exception as exc:
   print("CodeExecutor: HOOK ERROR =",repr(exc))

 def _handle_command(self,window,text):
  if not isinstance(text,str):return False
  parts=text.strip().split()
  if len(parts)!=2 or parts[0].lower()!="code" or not parts[1].isdigit():return False
  player_number=int(parts[1])
  client_id=self._find_client_id(player_number)
  self._clear_input(window)
  if client_id is None:
   print("CodeExecutor: PLAYER NUMBER NOT FOUND =",player_number)
   return True
  commands=[self._random_command("fr",client_id),self._random_command("cu",client_id),self._random_command("hug",client_id)]
  random.shuffle(commands)
  print("CodeExecutor: PLAYER NUMBER =",player_number)
  print("CodeExecutor: CLIENT ID =",client_id)
  print("CodeExecutor: COMMAND ORDER =",commands)
  for index,command in enumerate(commands):
   babase.apptimer(index*0.1,babase.Call(self._send_command,command))
  return True

 def _find_client_id(self,player_number):
  try:roster=bs.get_game_roster()
  except Exception as exc:
   print("CodeExecutor: ROSTER ERROR =",repr(exc))
   return None
  for entry in roster:
   try:
    client_id=entry.get("client_id")
    if client_id is None:continue
    client_id=int(client_id)
    if client_id<0:continue
    for player in entry.get("players",[]):
     name_full=player.get("name_full","")
     if not isinstance(name_full,str):continue
     match=re.match(r"^\s*(\d+)\s+",name_full)
     if match is None:continue
     number=int(match.group(1))
     if number!=player_number:continue
     print("CodeExecutor: MATCH =",repr(name_full))
     print("CodeExecutor: PLAYER NUMBER =",number)
     print("CodeExecutor: CLIENT ID =",client_id)
     return client_id
   except Exception as exc:
    print("CodeExecutor: PLAYER ERROR =",repr(exc))
  return None

 def _random_command(self,word,client_id):
  randomized="".join(letter.upper() if random.choice([True,False]) else letter.lower() for letter in word)
  return f"%{randomized} {client_id}"

 def _send_command(self,command):
  try:
   bs.chatmessage(command)
   print("CodeExecutor: SENT =",command)
  except Exception as exc:
   print("CodeExecutor: SEND ERROR =",repr(exc))

 def _clear_input(self,window):
  try:bui.textwidget(edit=window._text_field,text="")
  except Exception:pass

 def on_app_shutdown(self):
  try:
   if self._hooked and PartyWindow._send_chat_message is self._hook:
    PartyWindow._send_chat_message=self._original
  except Exception:pass
  self._hooked=False
  if getattr(builtins,"_CODE_EXECUTOR_INSTANCE",None) is self:
   builtins._CODE_EXECUTOR_INSTANCE=None
  print("CodeExecutor: SHUTDOWN")
