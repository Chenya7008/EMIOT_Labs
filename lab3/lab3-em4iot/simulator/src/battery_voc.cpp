#include "battery_voc.h"


void battery_voc::set_attributes()
{
    v_oc.set_timestep(SIM_STEP, sc_core::SC_SEC);
    r_s.set_timestep(SIM_STEP, sc_core::SC_SEC);
    soc.set_timestep(SIM_STEP, sc_core::SC_SEC);
    r_s.set_delay(1);
    soc.set_delay(1);
}

void battery_voc::initialize() {}

void battery_voc::processing()
{
    double tmpcurrent; // Battery current, if negative, the battery is charged 
    
    // Read input current
    tmpcurrent = i.read(); // Battery current, if negative, the battery is charged 

    /* 
    Compute actual state-of-charge solving the integral:
    SOC_t = SOC_{t-1} - \int^{t}_{-inf} i(\tau) / C d\tau
    */
    double c_nom = 3200.0; // mAh, Nominal Capacity
    tmpsoc -= (((tmpcurrent + prev_i_batt) * SIM_STEP) / (2 * 3600 * c_nom)); // 3600 * Cnom, mAh to mAs cause [sim step] = [s]
    prev_i_batt = tmpcurrent; // Update

    // Each instant the battery self-discharge a bit
    tmpsoc = (1.0 - SELFDISCH_FACTOR) * tmpsoc;

    // Output the battery SOC
    if(tmpsoc >= 1) // Not let the SOC overflow
    {
        soc.write(1);
        tmpsoc = 1;
    }
    else
    {
        soc.write(tmpsoc);
    }

    // SOC and battery Voc relationship
    double val_voc = -18.64842845 * pow(tmpsoc, 4) 
                     + 44.69486002 * pow(tmpsoc, 3) 
                     - 36.60037106 * pow(tmpsoc, 2) 
                     + 12.55851751 * tmpsoc 
                     + 2.05464539;
                     
    v_oc.write(val_voc); // 将计算结果写入端口
     double val_rs = -0.00045524 * pow(tmpsoc, 4) 
                    + 0.00116024 * pow(tmpsoc, 3) 
                    - 0.00091822 * pow(tmpsoc, 2) 
                    + 0.000177   * tmpsoc 
                    + 0.00010329;
                    
    r_s.write(val_rs); // 将计算结果写入端口

    // When the battery SOC decreases under 1%, the simulation stops.	
    if(tmpsoc <= 0.01)
    {
        cout << "SOC is less than or equal to 1%:" << " @" << sc_time_stamp() << endl;
        sc_stop();
    }
}
