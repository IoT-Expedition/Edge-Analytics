package com.example.deeplinkapp;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;

import java.util.List;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Uri data = getIntent().getData();
        String scheme = data.getScheme();

        if(scheme.equals("callschema")){
            String phoneNum = data.getQueryParameter("phone");
            Intent callIntent = new Intent(Intent.ACTION_DIAL);
            callIntent.setData(Uri.parse("tel:" + phoneNum));
            startActivity(callIntent);
        }

        else if (scheme.equals("textschema")){
            String phoneNum = data.getQueryParameter("phone");
            Intent smsIntent = new Intent(Intent.ACTION_VIEW);
            smsIntent.setType("vnd.android-dir/mms-sms");
            smsIntent.putExtra("address", phoneNum);
            smsIntent.putExtra("sms_body","");
            startActivity(smsIntent);
        }

        else{
            String mailID = data.getQueryParameter("mail");
            Intent mailIntent = new Intent(Intent.ACTION_VIEW);
            mailIntent.setType("plain/text");
            mailIntent.setData(Uri.parse(mailID));
            mailIntent.setClassName("com.google.android.gm", "com.google.android.gm.ComposeActivityGmail");
            mailIntent.putExtra(Intent.EXTRA_SUBJECT, "Knocker Test");
            mailIntent.putExtra(Intent.EXTRA_TEXT, "" +
                    "Message Body");
            startActivity(mailIntent);
        }

    }

    @Override
    protected void onResume(){
        super.onResume();
        finish();
    }

    @Override
    protected void onDestroy(){
        super.onDestroy();
    }

}
