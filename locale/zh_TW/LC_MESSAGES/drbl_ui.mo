��    .      �  =   �      �  "   �          -     H  #   f     �  ?   �  ,   �  �      �     �     �     �     �     �     �     �     �     	     	  	   	  	   	  	   )	     3	  
   8	     C	     H	     T	     ]	     b	     i	     o	     t	     �	     �	     �	     �	     �	     �	     �	     �	     �	     �	     
     
  4  
  -   K  !   y      �  3   �  !   �       ;   2  C   n    �    �     �     �     �     �     �               &     3     :     A     Y     q     �     �     �     �     �     �     �     �     �     �               #     *     1     I     V     g     p     |     �     �           $                                  ,       
      )   *                #                    .      &   (               -                 '                        %                 "          !   	      +    
	Step 1: Setup the Linux Server
	 
	Step 1a: Setup linux
	 
	Step 1b: Setup Network
	 
	Step 2: Setup the clients
	 
	Step 2a: Install program "drbl"
	 
	Step 2b: do drblsrv -i
	 
	Step 3: Set up the file system for the client in the Server
	 
	Step 4: Setting up clients to use the DRBL 
	The client has a PXE network interface card

	  * Set the client's BIOS to boot from "LAN" or "network".

	  * Take one of the Asus motherboards for example,

	      1. You will see OnBoard LAN, there is a subfuncton 
		 "OnBoard LAN BOOT ROM", normally it's disabled, 
		 you have to enable it.
	      2. Usually you have to reboot it now, make the 
		 function re-read by BIOS.
	      3. After rebooting, enter BIOS setting again, this time, 
		 you have to make LAN boot as the 1st boot device.

	The client do not support PXE network interface card
	Please check http://drbl.sourceforge.net

	That's it. Let client boot and enjoy DRBL!!! 

	Welcome to Diskless Remote Boot in Linux (DRBL)
	
	Please follow the steps for DRBL Environment

	Step1: Setup the Linux Server
	
	Step2: Setup the clients
	
	Step3: Set up the file system for the client in the Server
	
	Step4: Setting up clients to use the DRBL environment
	 Abort About Add User Apply Cancel Config Network Del User Diskless Remote Boot in Linux Finish Install Linux-gra Linux-txt List User Load Netinstall Next PXE BG MODE PXE MENU Quit Reboot Reset Save Select mode for Clonezilla Select mode for DRBL  Shutdown Start Stop Terminal Wake On Lan drbl-assistant drblpush drblsrv install drblsrv uninstall local memtest Project-Id-Version: drbl_ui 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2010-07-23 16:52+0800
PO-Revision-Date: 2010-07-11 22:00+0800
Last-Translator: thomas <thomas@nchc.org.tw>
Language-Team: Chinese (traditional)
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 
	步驟一、安裝您的 GNU/Linux 套件
	 
	步驟1a, 設定 Linux 主機
	 
	步驟1b, 設定主機網路
	 
	步驟二、在 server 上相關套件的安裝
	 
	步驟2a, 安裝DRBL主程式
	 
	步驟2b, 進行 drbldrv -i
	 
	步驟三、在 server 上建置 client 的檔案系統
	 
	步驟四、讓client端(也就是學生用的機器)網路開機 
	用戶端機器的網卡有PXE網路開機功能
	將用戶端電腦的BIOS設定成網路開機就可以當DRBL client了。
	2003年以後新購的電腦，主機板內建的網卡幾乎都有PXE功能，
	把PXE網路開機功能開啟。請參考你的主機板手冊為準。

	一般設定方式：
	BIOS->Advanced->Onboard Devices Configuration 
	->Onboard LAN->Onboard LAN Boot Rom->Enabled。

	另外，以下建議調整，以方便由DRBL server集中管理: 

	(1) Boot order設成優先順序為LAN -> CDROM -> HD 
	(2)開啟Wake on LAN (可能在APM Configuration 
	-> Power On By PCI Devices)。

	如果不支援，請參考DRBL網頁說明。
	設定設好後，把用戶端的電腦開機，正常的話，
	您應該可以看到用戶端電腦已經開機進去了X-window了 

	DRBL 安裝助手
	
	請依照以下步驟完成安裝

	Step1: 安裝您的 GNU/Linux 套件
	
	Step2: 在 server 上相關套件的安裝
	
	Step3: 在 server 上建置 client 的檔案系統
	
	Step4: 讓client端(也就是學生用的機器)網路開機
	 關於 關於 增加使用者 套用 取消 修改網路設定 刪除使用者 無碟系統 完成 安裝 無碟Linux圖形介面 無碟Linux文字介面 使用者列表 載入 提供網路安裝套件 繼續 開機選單介面 開機選單 離開 重新開機 重設 存檔 選擇 Clonezilla 模式 選擇 DRBL 模式 遠端關機 開始 停止 用戶端Terminal介面 網路開機 DRBL安裝助手 drblpush 安裝 DRBL 移除 DRBL 用戶端硬碟開機 用戶端記憶體測試 