��    >        S   �      H  ]   I  d   �  ^     R   k  T   �  "        6     O     j  #   �     �  ?   �  ,     �  4    �
     �     �     �     �     �  W   �  T   J  2   �     �     �  $   �            	     	   (  	   2     <  
   A     L     Q     ]     f     k     r     �  #   �  5   �                    '     =     F     `     f     k  ,   t  0   �  '   �     �                    .     @     F  4  N  7   �  0   �  =   �  =   *  :   h  -   �  !   �      �  3     !   H     j  ;   �  C   �    
    (     /     6     =     M     T  *   [  *   �  $   �     �     �     �                    3     K     [     b     {     �     �     �     �     �  !   �  !   �  6        M     T     [     t     �     �     �     �     �  $   �  $   �          6     C     T     ]     i     u     �                
          1                 -       +   	          2      .      ,          #         0          :          >      '       $                   3   7   ;          8   /   (             )          4   *   5       &      6   %         !       <      "   =   9                                 
	    Start to config drbl environment with drblpush
	    Please check all option here:
	     
	    Start to install DRBL and related packages by drblsrv
	    Please check all option here:
	     
	    To hide, reveal or set default PXE client menu:
	    Please check all option here:
	     
	    To set the default PXE client menu:
	    Please check all option here:
	     
	    Uninstall DRBL and data by drblsrv -u
	    Please check all option here:
	     
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
	 Abort About Add User Apply Cancel Client machine will boot from DRBL server, and enter graphic mode, for powerful client. Client machine will boot from DRBL server, and enter text mode, for powerful client. Client machine will boot from local (now PXE only) Config Network Del User Diskless Remote Boot in Linux (DRBL) Finish Install Linux-gra Linux-txt List User Load Netinstall Next PXE BG MODE PXE MENU Quit Reboot Reboot DRBL clients now Remote boot to run memtest86 Remote display Linux, terminal mode Remove NetworkManager and Install gnome-network-admin Reset Save Select mode for Clonezilla Select mode for DRBL  Shutdown Shutdown DRBL clients now Start Stop Terminal Thanks donate from Hualien county government Thanks for donate from Hualien county government Turn on DRBL clients by Wake-on-LAN now Wake On Lan drbl-assistant drblpush drblsrv install drblsrv uninstall local memtest Project-Id-Version: drbl_ui 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2010-07-26 17:09+0800
PO-Revision-Date: 2010-07-11 22:00+0800
Last-Translator: thomas <thomas@nchc.org.tw>
Language-Team: Chinese (traditional)
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 
	   在 server 上建置 client 的檔案系統

	     
	    在 server 上相關套件的安裝

	     
	    設定PXE項目選單
	    請設定以下選項:
	     
	    設定PXE選單介面
	    請設定以下選項:
	     
	   移除DRBL相關套件與用戶端檔案系統

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
	 關於 關於 增加使用者 套用 取消 用戶端機器設定為無碟圖形模式 用戶端機器設定為無碟文字模式 用戶端設定為本機開機模式 修改網路設定 刪除使用者 無碟系統 (DRBL) 完成 安裝 無碟Linux圖形介面 無碟Linux文字介面 使用者列表 載入 提供網路安裝套件 繼續 開機選單介面 開機選單 離開 重新開機 重新啟動用戶端機器 用戶端設定為記憶體測試 用戶端設定為終端機模式 是否移除NetworkManager並安裝gnome-network-admin 重設 存檔 選擇 Clonezilla 模式 選擇 DRBL 模式 遠端關機 關閉用戶端機器 開始 停止 用戶端Terminal介面 感謝花蓮縣政府贊助本專案 感謝花蓮縣政府贊助本專案 網路啟動用戶端機器 網路開機 DRBL安裝助手 drblpush 安裝 DRBL 移除 DRBL 用戶端硬碟開機 用戶端記憶體測試 