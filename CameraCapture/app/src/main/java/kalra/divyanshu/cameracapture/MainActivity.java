package kalra.divyanshu.cameracapture;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.Camera;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    Camera camera;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if(checkCameraHardware(this)){
            Toast.makeText(MainActivity.this, "Has Camera", Toast.LENGTH_SHORT).show();
            camera = getCameraInstance(MainActivity.this, this);

        }
        else
        {
            Toast.makeText(MainActivity.this, "No Camera.", Toast.LENGTH_SHORT).show();
        }
    }
    /** Check if this device has a camera */
    private boolean checkCameraHardware(Context context) {
        if (context.getPackageManager().hasSystemFeature(PackageManager.FEATURE_CAMERA))
            // this device has a camera
            return true;
            // no camera on this device
            return false;

    }
    public static Camera getCameraInstance(Context context, Activity activity){
        Camera c = null;
        int permissionCheck = ContextCompat.checkSelfPermission(context,
                Manifest.permission.CAMERA);
        ActivityCompat.requestPermissions(activity,
                new String[]{Manifest.permission.CAMERA},
                permissionCheck);
        try {
            c = Camera.open(); // attempt to get a Camera instance
        }
        catch (Exception e){
            // Camera is not available (in use or does not exist)

            Log.v("wow","Divesh is a pussy, who has no pussy.");//Divesh annoyed me so I put this.
        }
        return c; // returns null if camera is unavailable
    }
    public void OnClick(View view){
        int permissionCheck = ContextCompat.checkSelfPermission(MainActivity.this,
                Manifest.permission.CAMERA);
        ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.CAMERA},
                permissionCheck);
        Log.v("WOW", ""+permissionCheck);
        if(permissionCheck != -1) {
            Intent myIntent = new Intent(MainActivity.this,
                    CameraActivity.class);
            startActivity(myIntent);
        }
        else
        {
            Toast.makeText(MainActivity.this, "WOW", Toast.LENGTH_SHORT).show();
        }
    }
}
