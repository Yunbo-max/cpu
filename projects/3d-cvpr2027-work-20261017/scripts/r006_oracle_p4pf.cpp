#include "eccv2026/eccv2026.h"
#include "PoseLib/solvers/p3p.h"
#include "PoseLib/solvers/p4pf.h"

#include <Eigen/Core>
#include <Eigen/Geometry>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

namespace {
constexpr double kFocal = 525.0;
constexpr double kPi = 3.14159265358979323846;
struct Match { Eigen::Vector3d X, n; Eigen::Vector2d y; double ar, aq; };
struct Pair { int id; Eigen::Matrix3d Rgt, Rxz; Eigen::Vector3d tgt; std::vector<Match> m; };
struct Model { bool valid=false; Eigen::Matrix3d R; Eigen::Vector3d t; double f=0; int inliers=0; double med=INFINITY; };

std::vector<double> split_numbers(const std::string &line) {
    std::vector<double> out; std::stringstream ss(line); std::string x;
    while (std::getline(ss,x,',')) out.push_back(std::stod(x)); return out;
}
double rotation_error(const Eigen::Matrix3d &a,const Eigen::Matrix3d &b) {
    double x=((a*b.transpose()).trace()-1.0)/2.0; x=std::max(-1.0,std::min(1.0,x)); return std::acos(x)*180.0/kPi;
}
bool finite_model(const Eigen::Matrix3d &R,const Eigen::Vector3d &t,double f) {
    return R.allFinite()&&t.allFinite()&&std::isfinite(f)&&f>50&&f<2000&&std::abs(R.determinant()-1.0)<1e-4&&
           (R.transpose()*R-Eigen::Matrix3d::Identity()).cwiseAbs().maxCoeff()<1e-4;
}
std::pair<int,double> score(const Pair &p,const Eigen::Matrix3d &R,const Eigen::Vector3d &t,double f) {
    std::vector<double> e; for(const auto &m:p.m){ Eigen::Vector3d q=R*m.X+t; if(q(2)<=0) continue;
        Eigen::Vector2d z=f*q.head<2>()/q(2); double d=(z-m.y).norm(); if(d<=3.0)e.push_back(d); }
    if(e.empty()) return {0,INFINITY}; std::nth_element(e.begin(),e.begin()+e.size()/2,e.end()); return {(int)e.size(),e[e.size()/2]};
}
void consider(Model &best,const Pair&p,const Eigen::Matrix3d&R,const Eigen::Vector3d&t,double f){
    if(!finite_model(R,t,f))return; auto s=score(p,R,t,f); if(s.first>best.inliers||(s.first==best.inliers&&s.second<best.med)){
        best.valid=true;best.R=R;best.t=t;best.f=f;best.inliers=s.first;best.med=s.second;}}

std::tuple<Model,int> run_up2(const Pair&p,std::mt19937_64&rng){
    Model best;int valid=0;std::uniform_int_distribution<int>d(0,(int)p.m.size()-1);
    for(int h=0;h<512;++h){int a=d(rng),b=d(rng);if(a==b){--h;continue;} std::vector<Eigen::Matrix3d>Rs(2,Eigen::Matrix3d::Identity());
        std::vector<Eigen::Vector3d>ts(2,Eigen::Vector3d::Zero()),ns{p.m[a].n,p.m[b].n};std::vector<double>fs(2,1.0),ars{p.m[a].ar,p.m[b].ar},aqs{p.m[a].aq,p.m[b].aq},ds{p.m[a].X(2),p.m[b].X(2)};
        std::vector<Eigen::Vector2d>refs{p.m[a].X.hnormalized(),p.m[b].X.hnormalized()},ys{p.m[a].y,p.m[b].y};
        auto out=ECCV2026::solver_up2pf_ori(Rs,ts,fs,ars,aqs,refs,ds,ns,ys,p.Rxz);auto R=std::get<0>(out);auto t=std::get<1>(out);double f=std::get<2>(out);
        if(finite_model(R,t,f)){++valid;consider(best,p,R,t,f);} }
    return {best,valid};
}
std::tuple<Model,int> run_p3p(const Pair&p,std::mt19937_64&rng){
    Model best;int valid=0;std::uniform_int_distribution<int>d(0,(int)p.m.size()-1);
    for(int h=0;h<512;++h){int a=d(rng),b=d(rng),c=d(rng);if(a==b||a==c||b==c){--h;continue;}
        std::vector<Eigen::Vector3d>x,X;for(int i:{a,b,c}){Eigen::Vector3d q(p.m[i].y(0)/kFocal,p.m[i].y(1)/kFocal,1.0);x.push_back(q.normalized());X.push_back(p.m[i].X);}std::vector<poselib::CameraPose> poses;poselib::p3p(x,X,&poses);
        for(const auto &q:poses){auto R=q.R();if(finite_model(R,q.t,kFocal)){++valid;consider(best,p,R,q.t,kFocal);}}}
    return {best,valid};
}
std::tuple<Model,int> run_p4pf(const Pair&p,std::mt19937_64&rng){
    Model best;int valid=0;std::uniform_int_distribution<int>d(0,(int)p.m.size()-1);
    for(int h=0;h<512;++h){int a=d(rng),b=d(rng),c=d(rng),e=d(rng);
        if(a==b||a==c||a==e||b==c||b==e||c==e){--h;continue;}
        std::vector<Eigen::Vector2d>x;std::vector<Eigen::Vector3d>X;
        for(int i:{a,b,c,e}){x.push_back(p.m[i].y);X.push_back(p.m[i].X);}
        std::vector<poselib::CameraPose>poses;std::vector<double>focals;
        poselib::p4pf(x,X,&poses,&focals);
        for(size_t k=0;k<poses.size();++k){auto R=poses[k].R();double f=focals[k];
            if(finite_model(R,poses[k].t,f)){++valid;consider(best,p,R,poses[k].t,f);}}
    }
    return {best,valid};
}
void emit(int id,const char*arm,const Model&m,int valid,const Pair&p,double cpu){
    double re=INFINITY,ce=INFINITY,fe=INFINITY;if(m.valid){re=rotation_error(m.R,p.Rgt);ce=(-m.R.transpose()*m.t+p.Rgt.transpose()*p.tgt).norm();fe=std::abs(m.f-kFocal)/kFocal;}
    std::cout<<id<<','<<arm<<','<<(m.valid?1:0)<<','<<valid<<','<<m.inliers<<','<<m.med<<','<<re<<','<<ce<<','<<fe<<','<<m.f<<','<<cpu<<'\n';
}
}
int main(int argc,char**argv){if(argc!=3)return 2;std::map<int,Pair>ps;std::ifstream pf(argv[1]);std::string line;std::getline(pf,line);while(std::getline(pf,line)){
    auto v=split_numbers(line);Pair p;p.id=(int)v[0];int z=1;for(int i=0;i<3;i++)for(int j=0;j<3;j++)p.Rgt(i,j)=v[z++];for(int i=0;i<3;i++)p.tgt(i)=v[z++];for(int i=0;i<3;i++)for(int j=0;j<3;j++)p.Rxz(i,j)=v[z++];ps[p.id]=p;}
    std::ifstream mf(argv[2]);std::getline(mf,line);while(std::getline(mf,line)){auto v=split_numbers(line);int id=(int)v[0];Match m;m.X=Eigen::Vector3d(v[1],v[2],v[3]);m.y=Eigen::Vector2d(v[4],v[5]);m.ar=v[6];m.aq=v[7];m.n=Eigen::Vector3d(v[8],v[9],v[10]);ps[id].m.push_back(m);}
    std::cout<<"pair,arm,valid,valid_hypotheses,inliers,median_reproj_px,rotation_error_deg,center_error_m,focal_relative_error,focal_px,cpu_seconds\n"<<std::setprecision(17);
    for(auto &[id,p]:ps){if(p.m.size()<24)continue;std::mt19937_64 r1(0x4752415600000000ULL+id),r2(0x5034500000000000ULL+id);
        auto start=std::clock();auto [u,nu]=run_up2(p,r1);double cu=double(std::clock()-start)/CLOCKS_PER_SEC;
        start=std::clock();auto [b,nb]=run_p4pf(p,r2);double cb=double(std::clock()-start)/CLOCKS_PER_SEC;
        emit(id,"up2pf_ori_oracle",u,nu,p,cu);emit(id,"p4pf_unknown_focal",b,nb,p,cb);}return 0;}
