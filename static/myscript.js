window.onload = function(){
    imgLocation("container","album_box")
}

function imgLocation(parent,content){
    //将parent下所有的content全部取出
    var cparent = document.getElementById(parent);
    var ccontent = getChildElement(cparent,content);
    var imgWidth = ccontent[0].offsetWidth;
    var cols = Math.floor(940 /  imgWidth) ;

    var BoxHeightArr = [];
    for (var i = 0;i < ccontent.length;i++){

        if(i < cols){
            BoxHeightArr[i] = ccontent[i].offsetHeight;//即第一行的图片不需要改位置,只需要把图片高度放入数组参与有需要的比较
        }
        else{
            var minheight = Math.min.apply(null,BoxHeightArr);
            var minIndex = getminheightLocation(BoxHeightArr,minheight);//这里保存了最小高度的图片的序号
            //var mintop = ccontent[i].offsetTop;//mine
            //console.log(minheight);
            var mintop = ccontent[minIndex].offsetTop;
            //var minleft = ccontent[minIndex].offsetLeft;
            ccontent[i].style.position = "absolute";
            ccontent[i].style.top = minheight + mintop +  "px";
            ccontent[i].style.left = ccontent[minIndex].offsetLeft + "px";
            BoxHeightArr[minIndex] = BoxHeightArr[minIndex] + ccontent[i].offsetHeight;
        }
    }
    if(cols < ccontent.length) {
        //document.getElementById("bottom").style.cssText = "top:" + minheight + mintop +ccontent[ccontent.length-1].offsetHeight +"px";
        console.log(minheight+mintop+ccontent[ccontent.length-1].offsetHeight);
        console.log(ccontent[ccontent.length-1].offsetHeight);
        bottom_height=minheight+mintop+ccontent[ccontent.length-1].offsetHeight + 200;
        document.getElementById("bottom").style.top=bottom_height + "px";
        // document.getElementsBy("bottom").style.position="absolute";
        // document.getElementsByClassName("bottom").style.left="0 px";
        // document.getElementsByClassName("bottom").style.cssText="top:"+minheight + mintop+"px";
    }
    else{
        document.getElementById("bottom").style.bottom=5 + "px";
    }
    //这一段if的判断是为了控制页脚的位置,到现在改了这么多次之后,已经有点逻辑混乱了,有空再优化--0809

}

function getminheightLocation(BoxHeightArr,minHeight) {
    for (var i in BoxHeightArr){
        if(BoxHeightArr[i] == minHeight){
            return i;
        }
    }
}

function getChildElement(parent,content){
    var contentArr= [];
    var allcontent = parent.getElementsByTagName("*");
    for (var i = 0; i<allcontent.length;i++){
        if(allcontent[i].className==content){
            contentArr.push(allcontent[i]);
        }
    }
    return contentArr;
}