# Missing firmware functions - locoroco

**116 of 236 imported firmware functions have no registered handler** (120 have a registered handler, 50.8%). Registration is not proof of firmware fidelity. Names come from pspsdk where it declares the NID; other entries remain unnamed in this report.

`*` marks a missing handler observed in the sampled bring-up log. The log is rate-limited; this is not a complete reachability report or proof of the current blocker.

Regenerate: `tools/hle_coverage.py` (see README).

## Network (33)

| library | NID | function |
|---|---|---|
| sceNet | `0x50647530` | sceNetFreeThreadinfo |
| sceNet | `0x39AF39A6` | sceNetInit |
| sceNet | `0x281928A9` | sceNetTerm |
| sceNetAdhoc | `0xE1D621D7` | sceNetAdhocInit |
| sceNetAdhoc | `0x9DF81198` | sceNetAdhocPtpAccept |
| sceNetAdhoc | `0x157E6225` | sceNetAdhocPtpClose |
| sceNetAdhoc | `0xFC6FC07B` | sceNetAdhocPtpConnect |
| sceNetAdhoc | `0x9AC2EEAC` | sceNetAdhocPtpFlush |
| sceNetAdhoc | `0xE08BDAC1` | sceNetAdhocPtpListen |
| sceNetAdhoc | `0x877F6D66` | sceNetAdhocPtpOpen |
| sceNetAdhoc | `0x8BEA2B3E` | sceNetAdhocPtpRecv |
| sceNetAdhoc | `0x4DA4C788` | sceNetAdhocPtpSend |
| sceNetAdhoc | `0xA62C6F57` | sceNetAdhocTerm |
| sceNetAdhocMatching | `0xEA3C6108` | sceNetAdhocMatchingCancelTarget |
| sceNetAdhocMatching | `0x8F58BEDF` | sceNetAdhocMatchingCancelTargetWithOpt |
| sceNetAdhocMatching | `0xCA5EDA6F` | sceNetAdhocMatchingCreate |
| sceNetAdhocMatching | `0xF16EAF4F` | sceNetAdhocMatchingDelete |
| sceNetAdhocMatching | `0x2A2A1E07` | sceNetAdhocMatchingInit |
| sceNetAdhocMatching | `0x5E3D4B79` | sceNetAdhocMatchingSelectTarget |
| sceNetAdhocMatching | `0xB58E61B7` | sceNetAdhocMatchingSetHelloOpt |
| sceNetAdhocMatching | `0x93EF3843` | sceNetAdhocMatchingStart |
| sceNetAdhocMatching | `0x32B156B3` | sceNetAdhocMatchingStop |
| sceNetAdhocMatching | `0x7945ECDA` | sceNetAdhocMatchingTerm |
| sceNetAdhocctl | `0x20B317A0` | sceNetAdhocctlAddHandler |
| sceNetAdhocctl | `0x0AD043ED` | sceNetAdhocctlConnect |
| sceNetAdhocctl | `0x6402490B` | sceNetAdhocctlDelHandler |
| sceNetAdhocctl | `0x34401D65` | sceNetAdhocctlDisconnect |
| sceNetAdhocctl | `0x8DB83FDC` | sceNetAdhocctlGetPeerInfo |
| sceNetAdhocctl | `0x75ECD386` | sceNetAdhocctlGetState |
| sceNetAdhocctl | `0xE26F226E` | sceNetAdhocctlInit |
| sceNetAdhocctl | `0x9D689E13` | sceNetAdhocctlTerm |
| sceWlanDrv | `0x0C622081` | sceWlanGetEtherAddr |
| sceWlanDrv | `0xD7763699` | sceWlanGetSwitchState |

## Video / UMD (23)

| library | NID | function |
|---|---|---|
| sceMpeg | `0x874624D6` | sceMpegFinish |
| sceMpeg | `0x682A619B` | sceMpegInit |
| scePsmfPlayer | `0xF8EF08A6` | (not named in pspsdk) |
| scePsmfPlayer | `0x1078C008` | (not named in pspsdk) |
| scePsmfPlayer | `0x2BEB1569` | (not named in pspsdk) |
| scePsmfPlayer | `0x235D8787` | (not named in pspsdk) |
| scePsmfPlayer | `0x3EA82A4B` | (not named in pspsdk) |
| scePsmfPlayer | `0x1E57A8E7` | (not named in pspsdk) |
| scePsmfPlayer | `0x3D6D25A9` | (not named in pspsdk) |
| scePsmfPlayer | `0xDF089680` | (not named in pspsdk) |
| scePsmfPlayer | `0x95A84EE5` | (not named in pspsdk) |
| scePsmfPlayer | `0xE792CD94` | (not named in pspsdk) |
| scePsmfPlayer | `0x9B71A274` | (not named in pspsdk) |
| scePsmfPlayer | `0xB9848A74` | (not named in pspsdk) |
| scePsmfPlayer | `0xA0B8CA55` | (not named in pspsdk) |
| scePsmfPlayer | `0x46F61F8B` | (not named in pspsdk) |
| sceUmdUser | `0xC6183D47` | sceUmdActivate * |
| sceUmdUser | `0x6AF9B50A` | sceUmdCancelWaitDriveStat |
| sceUmdUser | `0xE83742BA` | sceUmdDeactivate |
| sceUmdUser | `0x6B4A146C` | sceUmdGetDriveStat * |
| sceUmdUser | `0xAEE7404D` | sceUmdRegisterUMDCallBack * |
| sceUmdUser | `0xBD2BDE07` | sceUmdUnRegisterUMDCallBack * |
| sceUmdUser | `0x8EF08FCE` | sceUmdWaitDriveStat * |

## Save / utility (20)

| library | NID | function |
|---|---|---|
| sceUtility | `0x946963F3` | sceUtilityGameSharingGetStatus |
| sceUtility | `0xC492F751` | sceUtilityGameSharingInitStart |
| sceUtility | `0xEFC6F80F` | sceUtilityGameSharingShutdownStart |
| sceUtility | `0x7853182D` | sceUtilityGameSharingUpdate |
| sceUtility | `0xA5DA2406` | sceUtilityGetSystemParamInt * |
| sceUtility | `0x34B78343` | sceUtilityGetSystemParamString |
| sceUtility | `0x1579A159` | sceUtilityLoadNetModule |
| sceUtility | `0x9A1C91D7` | sceUtilityMsgDialogGetStatus |
| sceUtility | `0x2AD8E239` | sceUtilityMsgDialogInitStart |
| sceUtility | `0x67AF3428` | sceUtilityMsgDialogShutdownStart |
| sceUtility | `0x95FC253B` | sceUtilityMsgDialogUpdate |
| sceUtility | `0x6332AA39` | sceUtilityNetconfGetStatus |
| sceUtility | `0x4DB1E739` | sceUtilityNetconfInitStart |
| sceUtility | `0xF88155F6` | sceUtilityNetconfShutdownStart |
| sceUtility | `0x91E70E35` | sceUtilityNetconfUpdate |
| sceUtility | `0x8874DBE0` | sceUtilitySavedataGetStatus |
| sceUtility | `0x50C4CD57` | sceUtilitySavedataInitStart |
| sceUtility | `0x9790B33C` | sceUtilitySavedataShutdownStart |
| sceUtility | `0xD4B95FFB` | sceUtilitySavedataUpdate |
| sceUtility | `0x64D50C56` | sceUtilityUnloadNetModule |

## Font (10)

| library | NID | function |
|---|---|---|
| sceLibFont | `0x3AEA8CB6` | sceFontClose |
| sceLibFont | `0x574B6FBC` | sceFontDoneLib |
| sceLibFont | `0x980F4895` | sceFontGetCharGlyphImage |
| sceLibFont | `0xDCC80C2F` | sceFontGetCharInfo |
| sceLibFont | `0x0DA7535E` | sceFontGetFontInfo |
| sceLibFont | `0xBC75D85B` | sceFontGetFontList |
| sceLibFont | `0x27F6E642` | sceFontGetNumFontList |
| sceLibFont | `0x67F17ED7` | sceFontNewLib |
| sceLibFont | `0xA834319D` | sceFontOpen |
| sceLibFont | `0xBB8E7FE6` | sceFontOpenUserMemory |

## Audio (9)

| library | NID | function |
|---|---|---|
| sceAtrac3plus | `0x7DB31251` | sceAtracAddStreamData |
| sceAtrac3plus | `0x6A8C3CD5` | sceAtracDecodeData |
| sceAtrac3plus | `0x780F88D1` | sceAtracGetAtracID |
| sceAtrac3plus | `0x36FAABFB` | sceAtracGetNextSample |
| sceAtrac3plus | `0x9AE849A7` | sceAtracGetRemainFrame |
| sceAtrac3plus | `0x5D268707` | sceAtracGetStreamDataInfo |
| sceAtrac3plus | `0x61EB33F5` | sceAtracReleaseAtracID |
| sceAtrac3plus | `0x0E2A73AB` | sceAtracSetData |
| sceAtrac3plus | `0x868120B5` | sceAtracSetLoopNum |

## System core (8)

| library | NID | function |
|---|---|---|
| LoadExecForUser | `0xBD2F1094` | sceKernelLoadExec |
| ModuleMgrForUser | `0x977DE386` | sceKernelLoadModule * |
| ModuleMgrForUser | `0xD675EBB8` | sceKernelSelfStopUnloadModule |
| ThreadManForUser | `0x8125221D` | sceKernelCreateMbx |
| ThreadManForUser | `0x86255ADA` | sceKernelDeleteMbx |
| ThreadManForUser | `0x0D81716A` | sceKernelPollMbx |
| ThreadManForUser | `0xE9B3061E` | sceKernelSendMbx |
| UtilsForUser | `0x6AD345D7` | sceKernelSetGPO |

## Input / display / GE (6)

| library | NID | function |
|---|---|---|
| sceCtrl | `0x3A622550` | sceCtrlPeekBufferPositive |
| sceCtrl | `0x0B588501` | sceCtrlReadLatch |
| sceDisplay | `0xEEDA2E54` | sceDisplayGetFrameBuf * |
| sceDisplay | `0x4D4E10EC` | sceDisplayIsVblank * |
| sceDisplay | `0x8EB9EC49` | sceDisplayWaitVblankCB * |
| sceDisplay | `0x984C27E7` | sceDisplayWaitVblankStart |

## Files (5)

| library | NID | function |
|---|---|---|
| IoFileMgrForUser | `0xB8A740F4` | sceIoChstat |
| IoFileMgrForUser | `0x54F5FB11` | sceIoDevctl |
| IoFileMgrForUser | `0xACE946E8` | sceIoGetstat |
| IoFileMgrForUser | `0x06A70004` | sceIoMkdir |
| IoFileMgrForUser | `0xF27A9C51` | sceIoRemove |

## Misc (2)

| library | NID | function |
|---|---|---|
| sceImpose | `0x36AA6E91` | sceImposeSetLanguageMode * |
| sceRtc | `0x3F7AD767` | sceRtcGetCurrentTick * |
